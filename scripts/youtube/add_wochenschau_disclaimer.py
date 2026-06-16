#!/usr/bin/env python3
"""
Wochenschau Disclaimer Tool
============================
Fügt Intro-Disclaimer und Wasserzeichen zu Wochenschau-Videos hinzu.

PFLICHT gemäß YouTube-Richtlinien:
"Der Kontext muss IN DEN BILDERN des Videos SELBST ersichtlich sein."

Usage:
    python add_wochenschau_disclaimer.py input.mp4 output.mp4
    python add_wochenschau_disclaimer.py input.mp4 output.mp4 --lang EN
"""

import subprocess
import sys
import os
from pathlib import Path

# Disclaimer-Texte
DISCLAIMER_DE = """⚠️ HISTORISCHES DOKUMENT

Dieses Video zeigt Original-Material
der NS-Propaganda-Wochenschau.

Es dient ausschließlich der
historischen Dokumentation und Bildung.

Die dargestellten Inhalte spiegeln
NICHT die Meinung des Uploaders wider."""

DISCLAIMER_EN = """⚠️ HISTORICAL DOCUMENT

This video contains original footage from
Nazi Germany's propaganda newsreels.

It is presented solely for historical
documentation and educational purposes.

The content shown does NOT reflect
the views of the uploader."""

WATERMARK_TEXT = "HISTORISCHES DOKUMENT • BILDUNGSZWECKE"


def create_disclaimer_video(output_path: str, duration: int = 7, lang: str = "DE"):
    """Erstellt ein Disclaimer-Intro-Video mit FFmpeg."""
    
    text = DISCLAIMER_DE if lang == "DE" else DISCLAIMER_EN
    
    # Escape für FFmpeg drawtext
    text_escaped = text.replace(":", "\\:").replace("'", "\\'")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi",
        "-i", f"color=c=black:s=3840x2160:d={duration}",
        "-vf", f"drawtext=text='{text_escaped}':fontcolor=white:fontsize=72:x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=20",
        "-c:v", "libx264",
        "-t", str(duration),
        output_path
    ]
    
    print(f"Erstelle Disclaimer-Video ({lang})...")
    subprocess.run(cmd, check=True)
    print(f"✅ Disclaimer erstellt: {output_path}")


def add_watermark(input_path: str, output_path: str):
    """Fügt permanentes Wasserzeichen hinzu."""
    
    text = WATERMARK_TEXT.replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-vf", f"drawtext=text='{text}':fontcolor=white@0.7:fontsize=36:x=20:y=20",
        "-c:a", "copy",
        output_path
    ]
    
    print("Füge Wasserzeichen hinzu...")
    subprocess.run(cmd, check=True)
    print(f"✅ Wasserzeichen hinzugefügt: {output_path}")


def concat_videos(intro_path: str, main_path: str, output_path: str):
    """Fügt Intro vor das Hauptvideo."""
    
    # Erstelle temporäre Dateiliste
    list_file = "temp_concat_list.txt"
    with open(list_file, "w") as f:
        f.write(f"file '{intro_path}'\n")
        f.write(f"file '{main_path}'\n")
    
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        output_path
    ]
    
    print("Füge Intro hinzu...")
    subprocess.run(cmd, check=True)
    os.remove(list_file)
    print(f"✅ Videos zusammengefügt: {output_path}")


def process_wochenschau(input_path: str, output_path: str, lang: str = "DE"):
    """
    Hauptfunktion: Fügt Disclaimer + Wasserzeichen hinzu.
    
    Args:
        input_path: Pfad zum Original-Video
        output_path: Pfad für das fertige Video
        lang: DE oder EN für Disclaimer-Sprache
    """
    
    print("=" * 60)
    print("WOCHENSCHAU DISCLAIMER TOOL")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print(f"Sprache: {lang}")
    print()
    
    # Temp-Dateien
    temp_dir = Path("temp_disclaimer")
    temp_dir.mkdir(exist_ok=True)
    
    disclaimer_path = temp_dir / f"disclaimer_{lang}.mp4"
    with_watermark_path = temp_dir / "with_watermark.mp4"
    
    try:
        # 1. Disclaimer-Intro erstellen (falls nicht vorhanden)
        if not disclaimer_path.exists():
            create_disclaimer_video(str(disclaimer_path), duration=7, lang=lang)
        
        # 2. Wasserzeichen zum Original hinzufügen
        add_watermark(input_path, str(with_watermark_path))
        
        # 3. Intro + Video zusammenfügen
        concat_videos(str(disclaimer_path), str(with_watermark_path), output_path)
        
        print()
        print("=" * 60)
        print("✅ FERTIG!")
        print(f"Output: {output_path}")
        print()
        print("⚠️  Vor Upload prüfen:")
        print("  □ Intro-Disclaimer sichtbar (7 Sek)?")
        print("  □ Wasserzeichen durchgehend lesbar?")
        print("  □ Category = Education (27)?")
        print("  □ Made for Kids = NEIN?")
        print("=" * 60)
        
    finally:
        # Temp aufräumen
        if with_watermark_path.exists():
            with_watermark_path.unlink()


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        print("\nBeispiel:")
        print("  python add_wochenschau_disclaimer.py wochenschau_477.mp4 output_477.mp4")
        print("  python add_wochenschau_disclaimer.py wochenschau_477.mp4 output_477.mp4 --lang EN")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    lang = "DE"
    
    if "--lang" in sys.argv:
        idx = sys.argv.index("--lang")
        if idx + 1 < len(sys.argv):
            lang = sys.argv[idx + 1].upper()
    
    if not os.path.exists(input_path):
        print(f"❌ Fehler: Datei nicht gefunden: {input_path}")
        sys.exit(1)
    
    process_wochenschau(input_path, output_path, lang)


if __name__ == "__main__":
    main()
