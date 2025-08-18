import csv
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import tkinter as tk
from tkinter import messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================== Entity-Klassen =========================

class Student:

    """
    Repräsentiert Student mit Name und Matrikelnummer.
    Klasse stellt Basisdaten bereit, die von anderen 
    Klassen (folgend Studiengang) verwendet werden können.
    """
    def __init__(self, eingabe_name, eingabe_matrikelnummer):
        self.name = eingabe_name
        self.matrikelnummer = eingabe_matrikelnummer

    @property
    def daten(self):
        """
        Gibt Basisdaten des Studenten als Dictionary zurück.
        """
        return {
            "Name": self.name,
            "Matrikelnummer": self.matrikelnummer
        }


class Studiengang:

    """
    Repräsentiert Studiengang des Studenten.
    Ist aggregiert mit Klasse "Student", bedeutet sie benötigt
    ein existierendes Student-Objekt.
    """
    def __init__(self, eingabe_student: Student, eingabe_studiengang, eingabe_abschluss, eingabe_datum_start):
        self.student = eingabe_student  # verknüftes Objekt -> Komposition: Studiengang ist darauf angewiesen, dass Student existiert
        self.studiengang = eingabe_studiengang
        self.abschluss = eingabe_abschluss
        self.datum_start = datetime.strptime(eingabe_datum_start, "%d.%m.%Y")  # Wandelt eingegebenes Startdatum in datetime-Objekt
        self.datum_ende = self.datum_start + timedelta(days=3*365)  # Setzt Studiendauer standardmäßig auf 3 Jahre

    @property
    def daten(self):
        """
        Enthält alle relevanten Informationen zum Studierenden und seinem Studiengang.
        Kombiniert Studenten- und Studiengangsdaten zu Dictionary und gibt es wieder.
        Kann damit einfach für CSV weiterverwendet werden.
        """
        daten_student = self.student.daten
        daten_studiengang = {
            "Studiengang": self.studiengang,
            "Abschluss": self.abschluss,
            "Startdatum": self.datum_start.strftime("%d.%m.%Y"), # Wandelt datetime-Objekt zurück in Str
            "Enddatum": self.datum_ende.strftime("%d.%m.%Y") # Wandelt datetime-Objekt zurück in Str
        }

        return {**daten_student, **daten_studiengang} # Zusammenführen beider Dictionarys


class Modul:

    """
    Repräsentiert ein Modul mit Bezeichnung, ECTS und Startdatum.
    Kann eigenständig bestehen und von Prüfungsleistung aggregiert werden.
    """
    def __init__(self, eingabe_bezeichnung, eingabe_ects, eingabe_datum_start):
        self.bezeichnung = eingabe_bezeichnung
        self.ects = eingabe_ects
        self.datum_start = datetime.strptime(eingabe_datum_start, "%d.%m.%Y")

    @property
    def daten(self):
        """
        Gibt Modul-Daten als Dictionary zurück.
        """
        return {
            "Modul": self.bezeichnung,
            "ECTS": self.ects,
            "Start": self.datum_start.strftime("%d.%m.%Y"),
        }


class Prüfungsleistung:

    """
    Repräsentiert Prüfungsleistung zu einem Modul.
    Aggregiert Modul, da ohne Modul keine Prüfungsleistung existiert.
    """
    def __init__(self, eingabe_modul: Modul, eingabe_datum_prüfung, note):
        self.modul = eingabe_modul # verknüftes Objekt -> Komposition: Prüfungsleistung ist darauf angewiesen, dass Modul existiert
        self.datum_prüfung = datetime.strptime(eingabe_datum_prüfung, "%d.%m.%Y") # Wandelt eingegebenes Startdatum in datetime-Objekt
        self.note = note
        self.tage_vorbereitung = (self.datum_prüfung - self.modul.datum_start).days  # berechnet Vorbereitungstage

    @property
    def daten(self):
        """
        Enthält alle relevanten Informationen zum Modul und dessen Prüfungsleistung.
        Kombiniert Modul- und Prüfungsleistungsdaten zu Dictionary und gibt es wieder.
        Kann damit einfach für CSV weiterverwendet werden.
        """
        daten_modul = self.modul.daten
        daten_prüfungsleistung = {
            "Ende": self.datum_prüfung.strftime("%d.%m.%Y"), # Wandelt datetime-Objekt zurück in Str
            "Note": self.note,
            "Tage": self.tage_vorbereitung
        }

        return {**daten_modul, **daten_prüfungsleistung} # Zusammenführen beider Dictionarys



# ============================== CSV-Klassen ============================

class CSV_Controller:
    """
    Verwaltet CSV-Dateien, zuständig für Speicherung von Studentendaten 
    und abgeschlossenen Modulen. Nutzt Entity-Klassen und erzeugt passende CSV-Struktur.
    """

    def __init__(self):
        self.datei_student = "Student.csv"
        self.datei_module = "Module_abgeschlossen.csv"

    def setze_student_csv(self, eingabe_name, eingabe_matrikelnummer, eingabe_studiengang, eingabe_abschluss, eingabe_datum_start):
        """
        Erstellt neue CSV-Datei mit Studentendaten mit nur einer Zeile.
        Speichert Ausgabe der Entity-Klassen Student + Studiengang als CSV.
        Überschreibt bei erneutem Aufruf den alten Eintrag.
        """
        self.student = Student(eingabe_name, eingabe_matrikelnummer)
        self.studium = Studiengang(self.student, eingabe_studiengang, eingabe_abschluss, eingabe_datum_start)

        spalten = ["Name", "Matrikelnummer", "Studiengang", "Abschluss", "Startdatum", "Enddatum"]
        neue_zeile = self.studium.daten

        # CSV neu erstellen, wenn vorhanden überschreiben
        with open(self.datei_student, mode="w", newline="", encoding="utf-8") as csv_1:
            writer = csv.DictWriter(csv_1, fieldnames=spalten)
            if csv_1.tell() == 0:
                writer.writeheader()
            writer.writerow(neue_zeile)

    def füge_modul_csv_hinzu(self, eingabe_name, eingabe_ects, eingabe_datum_start, eingabe_datum_prüfung, eingabe_note):
        """
        Fügt neuen Datensatz zu Modul und Prüfungsleistung in Modul-CSV ein.
        Erzeugt Eintrag einer Zeile mit Entity-Klassen Modul + Prüfungsleistung.
        Hängt Zeile an CSV an, sortiert diese anschließend nach Prüfungsdatum neu,
        sodass Zeilen und Modulabschlüsse chronologisch geordnet sind.
        (wichtig für spätere Diagramme)
        """
        self.modul = Modul(eingabe_name, eingabe_ects, eingabe_datum_start)
        self.prüfungsleistung = Prüfungsleistung(self.modul, eingabe_datum_prüfung, eingabe_note)

        spalten = ["Modul", "ECTS", "Start", "Ende", "Note", "Tage"]
        neue_zeile = self.prüfungsleistung.daten

        # Neue Zeile anhängen, wenn keine Datei vorhanden, neu erstellen
        with open(self.datei_module, mode="a", newline="", encoding="utf-8") as csv_2:
            writer = csv.DictWriter(csv_2, fieldnames=spalten)
            if csv_2.tell() == 0:
                writer.writeheader()
            writer.writerow(neue_zeile)

        # Datei neu sortieren nach Datum der Prüfung (Ende)
        einträge = []
        with open(self.datei_module, mode="r", encoding="utf-8") as csv_2:
            reader = csv.DictReader(csv_2)
            for zeile in reader:
                einträge.append(zeile)

        einträge.sort(key=lambda d: datetime.strptime(d["Ende"], "%d.%m.%Y"))

        with open(self.datei_module, mode="w", newline="", encoding="utf-8") as csv_2:
            writer = csv.DictWriter(csv_2, fieldnames=spalten)
            writer.writeheader()
            writer.writerows(einträge)

    def lösche_modul_csv(self, suchwert):
        """
        Löscht alle Einträge aus Modul-CSV, deren Modulname exakt dem Suchwert entspricht.
        """
        spalten = ["Modul", "ECTS", "Start", "Ende", "Note", "Tage"]
        spalte = "Modul"
        einträge = []

        # Nur Einträge übernehmen, die nicht Suchwert entsprechen
        with open(self.datei_module, mode="r", encoding="utf-8") as csv_2:
            reader = csv.DictReader(csv_2)
            for zeile in reader:
                if zeile.get(spalte) != suchwert:
                    einträge.append(zeile)

        # Datei mit bereinigten Einträgen neu schreiben
        with open(self.datei_module, mode="w", newline="", encoding="utf-8") as csv_2:
            writer = csv.DictWriter(csv_2, fieldnames=spalten)
            writer.writeheader()
            writer.writerows(einträge)



# ============================== Logik-Klasse ===========================

class Plots_Berechnungen:
    """
    Berechnungs- und Visualisierungsklasse.
    Verarbeitet CSV-Daten, erstellt statistische Auswertungen, Diagramme und Tabelle.
    Nutzt pandas, numpy und matplotlib (via Figure, für später flexible Anpassbarkeit in GUI).
    """

    def __init__(self):
        self.read_student_csv = pd.read_csv("Student.csv")
        self.read_module_csv = pd.read_csv("Module_abgeschlossen.csv")
        
        self.tage_vergangen = (datetime.today() - pd.to_datetime(self.read_student_csv.at[0, "Startdatum"], dayfirst=True)).days # berechnet vergangene Tage seit Studienstart
        self.ects_summe = self.read_module_csv["ECTS"].sum() # summiert bisher gesammelte ECTS-Punkte
        self.noten_schritte = [1.0, 1.3, 1.7, 2.0, 2.3, 2.7, 3.0, 3.3, 3.7, 4.0] # legt Notenschitte in Diagrammachsen fest

    def zahl_mittelwert_noten(self):
        """
        Berechnet Mittelwert aller Noten aus CSV und rundet auf 2 Nachkommastellen.
        """
        mittelwert = np.mean(self.read_module_csv["Note"])
        return round(mittelwert, 2)

    def zahl_abweichung_zeitplan(self):
        """
        Berechnet:
        - vergangene Tage seit Studienbeginn prozentual von Studiendauer 
        - erreichte ECTS-Punkten prozentual von gesamten ECTS-Punkten
        
        Vergleicht beide prozentualen Werte und gibt Abweichung zum Zeitplan
        in Tagen der Gesamtstudiendauer aus.
        Gibt positive oder negative Abweichung in Tagen als Text zurück.
        """
        self.fortschritt_zeit_prozentual = 100 / 1095 * self.tage_vergangen
        self.fortschritt_ects_prozentual = 100 / 180 * self.ects_summe
        
        abweichung = int(np.floor((self.fortschritt_ects_prozentual - self.fortschritt_zeit_prozentual) / 100 * 1095))

        if abweichung >= 0:
            return f"{abweichung} Tage vor dem Zeitplan" # f-Str nötig bei Ausgabe Variablen
        else:
            return f"{abweichung} Tage hinter dem Zeitplan"

    def plot_zeit_ects(self):
        """
        Erstellt horizontales Balkendiagramm mit:
        - vergangenen Tage seit Studienbeginn prozentual von Studiendauer 
        - erreichten ECTS-Punkten prozentual von gesamten ECTS-Punkten
        """
        tage_insgesamt = 1095
        ects_gesamt = 180

        werte = np.clip([
            (self.tage_vergangen / tage_insgesamt) * 100,
            (self.ects_summe / ects_gesamt) * 100
        ], 0, 100)

        labels = ["Zeit vergangen", "ECTS erreicht"]

        fig = Figure(figsize=(8, 1.5), dpi=90)
        ax = fig.add_subplot(111)
        ax.barh(labels, werte, color="black", alpha=0.8)
        ax.set_xlim(0, 100)
        ax.set_xlabel("Fortschritt in %")
        ax.invert_yaxis()
        fig.tight_layout()

        for i, v in enumerate(werte):
            ax.text(v + 1, i, f"{v:.1f}%", va="center") # zeigt Prozentwerte an

        return fig

    def plot_verteilung_noten(self):
        """
        Erstellt Histogramm der erreichten Noten (Häufigkeitsverteilung).
        """
        noten = self.read_module_csv["Note"]
        häufigkeit = noten.value_counts().reindex(self.noten_schritte, fill_value=0) # zählt Noten nach Schrittwerten

        fig = Figure(figsize=(4, 4), dpi=90)
        ax = fig.add_subplot(111)
        ax.bar(häufigkeit.index.astype(str), häufigkeit.values, color="#468FD7")
        ax.set_xlabel("Note")
        ax.set_ylabel("Häufigkeit")
        ax.set_xticklabels(häufigkeit.index.astype(str), rotation=45)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis="y")
        fig.tight_layout()

        return fig

    def plot_verlauf_noten(self):
        """
        Erstellt Liniendiagramm mit chronologischem Notenverlauf.
        Zeigt tatsächliche Noten und gleitenden Durchschnitt.
        """
        self.read_module_csv["Index"] = range(1, len(self.read_module_csv) + 1)
        noten = self.read_module_csv["Note"]
        durchschnitt_gleitend = noten.expanding().mean()

        fig = Figure(figsize=(4, 4), dpi=90)
        ax = fig.add_subplot(111)
        ax.plot(self.read_module_csv["Index"], noten, marker="o", label="Tatsächliche Note", color="black")
        ax.plot(self.read_module_csv["Index"], durchschnitt_gleitend, linewidth=4, alpha=0.3, label="Gleitender Durchschnitt", color="#468FD7")
        ax.set_xlabel("Modul (chronologisch)")
        ax.set_ylabel("Note")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_yticks(self.noten_schritte)
        ax.invert_yaxis()
        ax.grid(True)
        ax.legend()
        fig.tight_layout()

        return fig

    def plot_dauer_modul_semester(self):
        """
        Erstellt Balkendiagramm durchschnittlicher Bearbeitungstage für ein 
        Modul je Semester.

        Semester wird aus Differenz Tage zum Studienstart (alle 182 Tage) berechnet.
        Jedem Modul wird anhand seines Startdatums das jeweilige Semester zugeordnet.
        """ 
        
        # Liest "Studienstart" in Student.csv, konvertiert in datetime
        studium_start = datetime.strptime(self.read_student_csv["Startdatum"][0], "%d.%m.%Y")
        
        # Liest "Start" in Module_abgeschlossen.csv, konvertiert in datetime
        self.read_module_csv["Start"] = pd.to_datetime(self.read_module_csv["Start"], format="%d.%m.%Y")
        
        # ordnet jedem Modul in Module_abgeschlossen.csv ein Semester über fiktive Spalte "Semester" zu
        # Spalte "Semester" erscheint nicht real in CSV
        self.read_module_csv["Semester"] = ((self.read_module_csv["Start"] - studium_start).dt.days // 182) + 1

        # gruppiert alle Module in deren Semester und berechnet Gruppen-Durchschnitt
        durchschnitt = self.read_module_csv.groupby("Semester")["Tage"].mean()

        fig = Figure(figsize=(2, 7), dpi=90)
        ax = fig.add_subplot(111)
        ax.bar(durchschnitt.index, durchschnitt.values, color="#468FD7", width=0.6)
        ax.set_xlabel("Semester")
        ax.set_ylabel("Durchschn. Bearbeitungstage pro Modul je Semester")
        ax.set_xticks(durchschnitt.index)
        ax.grid(axis="y")
        fig.tight_layout()

        return fig

    def tabelle_module(self):
        """
        Erstellt Tabelle mit Modulen, Noten und Bearbeitungstagen.
        Zeigt nur relevante Spalten aus Modul-CSV.
        """
        module_csv_kurz = self.read_module_csv[["Modul", "Tage", "Note"]]

        fig = Figure(figsize=(3, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.axis('off')

        table = ax.table(
            cellText=module_csv_kurz.values,
            colLabels=module_csv_kurz.columns,
            loc='center',
            cellLoc='center'
        )

        # passt Spaltenbreite automatisch an und segt Schriftgröße fest
        table.auto_set_column_width(col=list(range(len(module_csv_kurz.columns))))
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        fig.tight_layout()

        return fig



# ============================== GUI-Klasse ============================== 

class GUI_Controller:
    """
    Controller-Klasse für grafische Benutzeroberfläche (GUI).
    Organisiert Aufbau, Inhalte, Interaktion und Button-Logik mit tkinter.
    """

    def __init__(self):
        """
        Initialisiert Hauptfenster und führt sofort Layout- und Inhalt aus.
        Mainloop startet direkt nach GUI-Erstellung.
        """
        self.root = tk.Tk()
        self.fenster()
        self.container_inhalt()
        self.container_interaktion()
        self.buttons()
        self.root.mainloop()

    def fenster(self):
        """
        Erstellt Fenster, setzt Titel aus Studentendaten.
        Legt Rasterstruktur (Grid), Ränder und Containerbereiche fest.
        """
        df = pd.read_csv("Student.csv")
        name = df.at[0, "Name"]
        studiengang = df.at[0, "Studiengang"]
        abschluss = df.at[0, "Abschluss"]
        titel = f"Dashboard Studium: {name} - {studiengang}, {abschluss}"

        self.root.title(titel)
        self.root.geometry("1200x800")

        # Fenster am Raster unterteilt für anpassbares Layout
        for i in range(20):
            self.root.grid_rowconfigure(i, weight=1)
        for j in range(30):
            self.root.grid_columnconfigure(j, weight=1)

        # Randfelder, feste Größe, farblos
        self.leer_links = tk.Frame(self.root, width=30)
        self.leer_rechts = tk.Frame(self.root, width=30)
        self.leer_oben = tk.Frame(self.root, height=30)
        self.leer_unten = tk.Frame(self.root, height=30)

        self.leer_links.grid(row=1, column=0, rowspan=19, columnspan=1)
        self.leer_rechts.grid(row=1, column=31, rowspan=19, columnspan=1)
        self.leer_oben.grid(row=0, column=0, rowspan=1, columnspan=31)
        self.leer_unten.grid(row=20, column=0, rowspan=1, columnspan=31)

        # Containerstruktur, aufteilung der Inhalte am flexiblen Raster, Hintergrundfarbe weiß
        self.container_oben = tk.Frame(self.root, bg="white")
        self.container_mitte = tk.Frame(self.root, bg="white")
        self.container_rechts = tk.Frame(self.root, bg="white")
        self.container_links = tk.Frame(self.root, bg="white")
        self.container_links_oben = tk.Frame(self.root, bg="white")
        self.container_links_unten_1 = tk.Frame(self.root, bg="white")
        self.container_links_unten_2 = tk.Frame(self.root, bg="white")
        self.container_links_unten_3 = tk.Frame(self.root, bg="white")
        self.container_unten = tk.Frame(self.root, bg="white")

        self.container_oben.grid(row=1, column=8, rowspan=2, columnspan=22, sticky="nsew")
        self.container_mitte.grid(row=3, column=8, rowspan=8, columnspan=17, sticky="nsew")
        self.container_rechts.grid(row=3, column=25, rowspan=17, columnspan=5, sticky="nsew")
        self.container_links.grid(row=3, column=1, rowspan=10, columnspan=7, sticky="nsew")
        self.container_links_oben.grid(row=1, column=1, rowspan=2, columnspan=7, sticky="nsew")
        self.container_links_unten_1.grid(row=13, column=1, rowspan=4, columnspan=2, sticky="nsew")
        self.container_links_unten_2.grid(row=13, column=3, rowspan=4, columnspan=5, sticky="nsew")
        self.container_links_unten_3.grid(row=17, column=1, rowspan=3, columnspan=7, sticky="nsew")
        self.container_unten.grid(row=11, column=8, rowspan=9, columnspan=17, sticky="nsew")

    def zeige_inhalt(self, fig, container):
        """
        Bindet Diagramm/Tabelle in jeweiligen Container ein. 
        (erleichtert folgend Einbindung)
        """
        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.get_tk_widget().pack(expand=True, fill="both")

    def container_inhalt(self):
        """
        Platziert Methoden für Texte/Diagramme/Tabelle aus Plots_Berechnungen 
        in Containern.
        """
        # Texte
        text_notenschnitt = f"Dein Notenschnitt: {Plots_Berechnungen().zahl_mittelwert_noten()}"
        text_zeitplan = f"Du bist {Plots_Berechnungen().zahl_abweichung_zeitplan()}."
        tk.Label(self.container_links_oben, text=text_notenschnitt, bg="white").pack(pady=20)
        tk.Label(self.container_links_oben, text=text_zeitplan, bg="white").pack(pady=0)
        
        # Diagramme/Tabelle
        self.zeige_inhalt(Plots_Berechnungen().plot_zeit_ects(), self.container_oben)
        self.zeige_inhalt(Plots_Berechnungen().plot_verteilung_noten(), self.container_mitte)
        self.zeige_inhalt(Plots_Berechnungen().plot_verlauf_noten(), self.container_unten)
        self.zeige_inhalt(Plots_Berechnungen().plot_dauer_modul_semester(), self.container_rechts)
        self.zeige_inhalt(Plots_Berechnungen().tabelle_module(), self.container_links)        

    def container_interaktion(self):
        """
        Erstellt Label und Eingabefelder für Modul, Start, Prüfung, Note.
        """
        # Label neben Eingabefeldern
        tk.Label(self.container_links_unten_1, text="Modul (Bezeichnung):", bg="white").pack(padx=10, pady=3, anchor="w")
        tk.Label(self.container_links_unten_1, text="Beginn (TT.MM.JJJJ):", bg="white").pack(padx=10, pady=3, anchor="w")
        tk.Label(self.container_links_unten_1, text="Prüfung (TT.MM.JJJJ):", bg="white").pack(padx=10, pady=3, anchor="w")
        tk.Label(self.container_links_unten_1, text="Note (N.N -> mit Punkt):", bg="white").pack(padx=10, pady=3, anchor="w")

        # Eingabefelder
        self.eingabe_modul = tk.Entry(self.container_links_unten_2)
        self.eingabe_modul.pack()

        self.eingabe_beginn = tk.Entry(self.container_links_unten_2)
        self.eingabe_beginn.pack()

        self.eingabe_prüfung = tk.Entry(self.container_links_unten_2)
        self.eingabe_prüfung.pack()

        self.eingabe_note = tk.Entry(self.container_links_unten_2)
        self.eingabe_note.pack()

    def funktion_button_hinzufügen(self):
        """
        Erstellt Hinzufügen-Funktion:
        Eingabe wird nur gespeichert, wenn alle Felder befüllt.
        Ruft CSV_Controller().füge_modul_csv_hinzu() für neuen Eintrag in CSV auf, 
        schließt und aktualisiert GUI.
        """
        if self.eingabe_note.get():
            CSV_Controller().füge_modul_csv_hinzu(
                self.eingabe_modul.get(),
                5,
                self.eingabe_beginn.get(),
                self.eingabe_prüfung.get(),
                float(self.eingabe_note.get())
            )
            self.root.destroy() # schließt GUI
            GUI_Controller() # öffnet GUI wieder (ermöglicht Aktualisierung Inhalte)
        else:
            messagebox.showwarning("Eingabefehler", "Bitte befülle alle vier Felder.")

    def funktion_button_löschen(self):
        """
        Erstellt Löschen-Funktion:
        Gewünschtes Modul wird entfernt, wenn korrektes Feld befüllt ist.
        Ruft CSV_Controller().lösche_modul_csv() auf und löscht gewünschte Zeile,
        schließt und aktualisiert GUI.
        """
        if self.eingabe_modul.get():
            CSV_Controller().lösche_modul_csv(self.eingabe_modul.get())
            self.root.destroy() # schließt GUI
            GUI_Controller() # öffnet GUI wieder (ermöglicht Aktualisierung Inhalte)
        else:
            messagebox.showwarning("Eingabefehler", "Bitte gib bei \"Modul (Bezeichnung):\" ein Modul ein, das du löschen möchtest.")

    def buttons(self):
        """
        Erstellt Buttons für Interaktion und verknüpft Hinzufügen-/Löschen-Funktion.
        """
        tk.Button(self.container_links_unten_3, text="Modul hinzufügen", command=self.funktion_button_hinzufügen, bg="white").pack()
        tk.Button(self.container_links_unten_3, text="Modul löschen", command=self.funktion_button_löschen, bg="white").pack(pady=12)




# ===#===#===#===#===#===#===#== Ausführung ==#===#===#===#===#===#===#==

# Ausführung der GUI
GUI_Controller()

# Eingaben für Student.csv hier tätigen -> ausreichend für konzeptionellen Zweck
# Kann theoretisch ebenfalls in GUI eingebunden werden.
CSV_Controller().setze_student_csv("Phillip Riemer", "UI123456", "Angewandte KI", "Bachelor of Science", "12.01.2025")
