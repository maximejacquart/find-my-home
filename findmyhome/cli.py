"""CLI entry point: run pipeline, save/list ads, generate application mails."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from . import config, filters, report, scoring, sources
from .db import Database
from .mailer import send_html


def cmd_run(args):
    cfg = config.load_global()
    db = Database(cfg["db_path"])
    users = config.list_users() if args.all_users else [args.user]
    if not users or users == [None]:
        sys.exit("Aucun utilisateur. Crée config/users/<nom>.yaml (voir example.yaml) ou passe --user.")

    for name in users:
        user = config.load_user(name)
        print(f"\n=== {name} ===")
        print("Collecte…")
        found = sources.fetch_all(user["sources"], user["filters"], cfg)

        new_count = 0
        for l in found:
            if db.upsert_listing(l):
                new_count += 1
        print(f"  total: {len(found)} collectées, {new_count} nouvelles")

        kept = filters.apply(found, user["filters"])
        print(f"Filtres durs: {len(kept)} retenues")

        already = db.already_reported(name)
        fresh = [l for l in kept if l.id not in already]
        print(f"Jamais présentées à {name}: {len(fresh)}")

        to_score = [l for l in fresh if db.get_score(l.id, name) is None]
        if to_score and not args.no_score:
            print(f"Scoring LLM de {len(to_score)} annonces…")
            results = scoring.score_listings(to_score, user["preferences"])
            for lid, r in results.items():
                db.set_score(lid, name, r["score"], r["verdict"], "|".join(r["flags"]))

        scored = []
        for l in fresh:
            s = db.get_score(l.id, name)
            if s:
                scored.append((l, {"score": s["score"], "verdict": s["verdict"],
                                   "flags": [f for f in (s["reasons"] or "").split("|") if f]}))
            elif args.no_score:
                scored.append((l, {"score": 50, "verdict": "(non scoré)", "flags": []}))
        scored.sort(key=lambda x: x[1]["score"], reverse=True)
        top = scored[: cfg["top_n"]]

        html = report.render(user, top, total_scanned=len(found), total_new=new_count,
                             sources=user["sources"])
        out_dir = Path(config.ROOT) / "out"
        out_dir.mkdir(exist_ok=True)
        out_file = out_dir / f"report-{name}.html"
        out_file.write_text(html, encoding="utf-8")
        print(f"Rapport écrit: {out_file}")

        sent = False
        if args.no_email:
            print("(envoi email désactivé)")
        else:
            to_addr = user.get("email")
            if not to_addr:
                print(f"  ! pas d'email dans config/users/{name}.yaml, envoi sauté")
            else:
                subject = f"🏠 Find My Home — {len(top)} offres pour toi cette semaine"
                send_html(cfg["smtp"], to_addr, subject, html)
                print(f"Email envoyé à {to_addr}")
                sent = True

        # only mark as seen once actually delivered, so dry-runs stay repeatable
        if sent:
            db.mark_reported([l.id for l, _ in top], name)


def cmd_save(args):
    cfg = config.load_global()
    db = Database(cfg["db_path"])
    listing = db.find_listing(args.listing_id)
    if not listing:
        sys.exit(f"Annonce introuvable ou ambiguë: {args.listing_id}")
    db.save_listing(listing.id, args.user, args.note or "")
    print(f"Sauvegardée pour {args.user}: {listing.title} — {listing.url}")


def cmd_unsave(args):
    cfg = config.load_global()
    db = Database(cfg["db_path"])
    listing = db.find_listing(args.listing_id)
    if not listing:
        sys.exit(f"Annonce introuvable: {args.listing_id}")
    db.unsave_listing(listing.id, args.user)
    print(f"Retirée des sauvegardes de {args.user}: {listing.title}")


def cmd_saved(args):
    cfg = config.load_global()
    db = Database(cfg["db_path"])
    items = db.saved_listings(args.user)
    if not items:
        print(f"Aucune annonce sauvegardée pour {args.user}.")
        return
    for listing, meta in items:
        print(f"[{meta['saved_at'][:10]}] {listing.id}")
        print(f"  {listing.title} — {listing.price}€ — {listing.city}")
        print(f"  {listing.url}")
        if meta.get("note"):
            print(f"  note: {meta['note']}")


def cmd_apply(args):
    from . import apply_mail
    cfg = config.load_global()
    db = Database(cfg["db_path"])
    listing = db.find_listing(args.listing_id)
    if not listing:
        sys.exit(f"Annonce introuvable: {args.listing_id}")
    user = config.load_user(args.user)
    print(f"Génération du mail de candidature pour: {listing.title}…")
    subject, body = apply_mail.generate(listing, user)
    out_dir = Path(config.ROOT) / "out"
    out_dir.mkdir(exist_ok=True)
    # listing.id comes from scraped third-party data; whitelist chars to keep
    # the filename inside out/ (no path separators, no ..).
    safe_id = re.sub(r"[^A-Za-z0-9_.-]", "_", listing.id)
    out_file = out_dir / f"candidature-{safe_id}.txt"
    if out_file.resolve().parent != out_dir.resolve():
        sys.exit("Nom de fichier de sortie invalide.")
    out_file.write_text(f"OBJET: {subject}\n\n{body}\n", encoding="utf-8")
    print(f"\nOBJET: {subject}\n\n{body}\n")
    print(f"→ enregistré dans {out_file}")


def cmd_users(_args):
    users = config.list_users()
    print("\n".join(users) if users else "Aucun utilisateur configuré.")


def main(argv=None):
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    p = argparse.ArgumentParser(prog="fmh", description="Find My Home — veille locative Bordeaux")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="collecte + score + rapport + email")
    r.add_argument("--user", help="utilisateur (config/users/<nom>.yaml)")
    r.add_argument("--all-users", action="store_true", help="tous les utilisateurs")
    r.add_argument("--no-email", action="store_true", help="ne pas envoyer, juste écrire out/report-*.html")
    r.add_argument("--no-score", action="store_true", help="sauter le scoring LLM")
    r.set_defaults(func=cmd_run)

    s = sub.add_parser("save", help="sauvegarder une annonce")
    s.add_argument("listing_id")
    s.add_argument("--user", required=True)
    s.add_argument("--note")
    s.set_defaults(func=cmd_save)

    u = sub.add_parser("unsave", help="retirer une annonce sauvegardée")
    u.add_argument("listing_id")
    u.add_argument("--user", required=True)
    u.set_defaults(func=cmd_unsave)

    ls = sub.add_parser("saved", help="lister les annonces sauvegardées")
    ls.add_argument("--user", required=True)
    ls.set_defaults(func=cmd_saved)

    a = sub.add_parser("apply", help="générer un mail de candidature")
    a.add_argument("listing_id")
    a.add_argument("--user", required=True)
    a.set_defaults(func=cmd_apply)

    sub.add_parser("users", help="lister les utilisateurs").set_defaults(func=cmd_users)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
