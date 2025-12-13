# Lastenheft

Dieses Lastenheft beschreibt die Anforderungen, die der Auftraggeber an das
zu entwickelnde Streaming‑Portal stellt. Es dient dem Team als Grundlage für
die weitere Planung und die spätere Umsetzung.

## 1  Zielsetzung

Der Auftraggeber betreibt einen eigenen YouTube‑Kanal mit hunderten bis
tausenden Videos und möchte diese in Form einer eigenen Mediathek
präsentieren. Ziel ist es, eine moderne Streaming‑Plattform zu entwickeln,
die optisch an bekannte Dienste wie Netflix, Waipu TV oder Apple TV erinnert
und sowohl auf Desktop‑Browsern als auch auf Tablets und anderen Geräten
optimal funktioniert.

Die Plattform soll:

1. **Alle eigenen YouTube‑Videos einbinden:** Die Videos werden nicht
   heruntergeladen oder selbst gehostet, sondern über die YouTube‑API
   eingebettet. Die Rechtsprechung erlaubt das Einbetten von öffentlich
   verfügbaren Videos【613967695887634†L418-L423】.
2. **Automatisch aktuell bleiben:** Neue Uploads des Kanals sollen
   automatisch erkannt und in die Mediathek einsortiert werden. Es wird
   erwartet, dass bis zu mehrere tausend Videos verwaltet werden können.
3. **Kategoriestruktur:** Die Inhalte sollen nach Jahren, Genres (Cartoons,
   Classics, Themen) oder speziellen Bereichen wie „Media Milestones“
   (wichtige historische Fernsehmomente) gegliedert werden können.
4. **Attraktives UI/UX:** Nutzer sollen die Inhalte leicht finden. Der
   Dienst soll eine „Continue Watching“-Sektion bereitstellen, damit
   laufende Videos schnell weitergesehen werden können【592209751761238†L65-L73】.
   Ein personalisierter Einstieg wie bei modernen Streaming‑Apps (z. B.
   unterschiedliche Profile) ist wünschenswert【592209751761238†L148-L176】.
5. **Plattformübergreifend:** Die Oberfläche soll responsive sein und
   Tablets, Desktop‑Bildschirme und eventuell Smart‑TVs unterstützen.
6. **Admin‑Bereich:** Der Auftraggeber benötigt ein Backend, um Videos
   manuell zu verwalten, Kategorien zu bearbeiten und Vorschläge zur
   Organisation anzunehmen oder abzulehnen.
7. **Livestream‑Integration:** Wenn ein YouTube‑Livestream stattfindet,
   soll er prominent eingeblendet werden; bei Inaktivität kann die
   Livestream‑Sektion entfallen. Es soll möglich sein, zukünftige Live
   Termine zu markieren.
8. **Zukunftssicherheit:** Die Plattform soll skalierbar sein und
   technische Neuerungen wie 8K‑Streaming (sofern YouTube dies ermöglicht)
   künftig unterstützen können.

## 2  Rahmenbedingungen und Randbedingungen

### 2.1  Rechtliche Anforderungen

- **Urheberrecht:** Nur eigene YouTube‑Videos werden eingebettet. Das
  Einbetten ist rechtlich zulässig, sofern die Videos öffentlich sind
  【613967695887634†L418-L423】.
- **YouTube‑Richtlinien:** Der YouTube‑Player muss gemäß den Nutzungs‑
  bedingungen verwendet werden. Viele Parameter zum Entfernen von
  Branding und Steuerelementen sind veraltet【612664126166649†L377-L451】,
  daher wird das YouTube‑Logo weiterhin sichtbar sein. Es wird jedoch
  angestrebt, die Integration so dezent wie möglich zu gestalten.
- **Datenschutz (DSGVO):** Durch das Einbetten des Players werden
  personenbezogene Daten an Google übermittelt. Ein Cookie‑Banner oder
  eine Zustimmungsabfrage ist zwingend notwendig. Die Verwendung des
  YouTube‑Players im sogenannten „YouTube‑NoCookie“-Modus wird geprüft.

### 2.2  Technische Rahmenbedingungen

- **Videoquelle:** Alle Videos liegen auf YouTube. Es werden keine
  eigenen Streaming‑Server oder extra Encodings betrieben. Die Plattform
  nutzt die YouTube Data API, um die Upload‑Playlist des Kanals
  abzurufen【391388008267651†L498-L537】 und via iFrame einzubetten.
- **Skalierbarkeit:** Das System muss tausende Inhalte verarbeiten.
  Dafür sind effiziente Datenbank‑Strukturen und Caching‑Mechanismen
  einzuplanen.
- **Mehrsprachigkeit:** Perspektivisch soll die Plattform auch andere
  Sprachen unterstützen (z. B. Deutsch/Englisch). Eine spätere
  Internationalisierung muss möglich sein.

### 2.3  Nutzungsbedingungen

- **Benutzerführung:** Besucher sollen ohne Registrierung Inhalte
  konsumieren können. Es besteht die Option, Profile oder Accounts
  hinzuzufügen, wenn mehrere Personen dieselbe Plattform nutzen.
- **Gestaltung:** Das Design soll mehrere Themes unterstützen (Netflix‑,
  Waipu‑ oder Apple‑ähnlich). Diese können je nach Zielgruppe oder
  Branding ausgewählt werden. Es ist nicht erlaubt, das YouTube‑Logo
  vollständig zu verstecken; ein dezentes „Powered by YouTube“ oder
  ähnlicher Hinweis wird akzeptiert.

## 3  Funktionale Anforderungen

1. **Video‑Auflistung:** Alle Videos des Kanals werden übersichtlich
   dargestellt, gruppiert nach Kategorien, Jahren, Genres usw.
2. **Suche und Filter:** Der Nutzer kann Videos nach Titel, Jahr,
   Länge, Kategorie oder Schlagwort durchsuchen.
3. **Continue Watching / Verlauf:** Wird ein Video begonnen, speichert
   die Plattform die Position (lokal oder serverseitig), damit der
   Nutzer später weiterschauen kann【592209751761238†L65-L73】.
4. **Anzeige neuer und beliebter Inhalte:** Es gibt eine Kategorie
   „Neu hinzugefügt“ sowie eine Darstellung der meistgesehenen Videos.
5. **Media Milestones:** Besondere Highlights (erste Sendungen, wichtige
   Fernsehmomente) werden hervorgehoben und im Bereich „Media
   Milestones“ zusammengestellt.
6. **Livestream‑Sektion:** Bei Live‑Streams soll ein permanenter Player
   angezeigt werden; andernfalls wird der Platz frei oder mit
   Standardinhalten gefüllt.
7. **Admin‑Funktionen:** Im Backend können Kategorien erstellt,
   bearbeitet, sortiert und Vorschläge des Systems geprüft werden. Es
   können manuell Metadaten hinzugefügt oder korrigiert werden (z. B.
   falsche Beschreibungen von YouTube).
8. **Automatische Aktualisierung:** Ein Cron‑Job ruft täglich die
   YouTube‑API auf, um neue Videos in die Datenbank zu importieren
   und bestehende Metadaten zu aktualisieren【391388008267651†L498-L537】.
9. **Mehrere Themes:** Der Nutzer oder Admin kann zwischen
   unterschiedlichen Layouts wählen (Netflix‑/Waipu‑/Apple‑Theme).

## 4  Nichtfunktionale Anforderungen

1. **Performance:** Die Seite soll auch bei tausenden Videos schnell
   reagieren. Caching und Lazy‑Loading von Bildern sind vorgesehen.
2. **Responsiveness:** Das UI ist responsive; es passt sich an
   verschiedene Bildschirmgrößen an.
3. **Barrierefreiheit:** Kontrastreiche Farben, große Schriften und
   Tastaturbedienbarkeit berücksichtigen barrierefreie Nutzung【33158469727155†L123-L167】.
4. **Sicherheit:** Das Backend muss gegen unautorisierte Zugriffe
   abgesichert werden; Nutzer‑Daten (falls vorhanden) sind zu
   verschlüsseln. Die Kommunikation erfolgt per HTTPS.
5. **Erweiterbarkeit:** Das System soll modular sein, damit weitere
   Quellen (z. B. Vimeo) oder zusätzliche Features (z. B. Paywall) später
   integriert werden können.

## 5  Abgrenzungskriterien

- Fremde Videos (von anderen YouTube‑Kanälen) werden nicht eingebunden.
- Es wird kein eigener Videoplayer entwickelt; der YouTube‑IFrame wird
  verwendet, um die Wiedergabe und Werbung abzuwickeln. Eingriffe in
  YouTube‑Werbung sind nicht vorgesehen.
- Offline‑Wiedergabe oder Download der Videos ist nicht Teil des Projekts.
- Multikanal‑Verwaltung (mehrere YouTube‑Kanäle) wird vorerst nicht
  unterstützt, kann aber später eingeplant werden.

---

*Dieses Lastenheft bildet die Basis für das Pflichtenheft, welches die
technische Umsetzung detailliert beschreibt.*