# Kandidatarbete-Chalmers-MCCX02-19-06
### Software defined radar för mätning av hjärt- och andningsfrekvens

#### Gå igenom följande steg för att använda GitHub på bästa sätt:

1. Skapa ett konto på GitHub https://github.com/
2. Ladda ner och installera Visual Studio Code https://code.visualstudio.com/
3. Ladda ner och installera Git https://git-scm.com/downloads Detta kan vara lite besvärligt. Välj Visual Studio Code som editor. I de flesta fall kan man bara trycka ok eller next.
4. Ladda ner och installera GitHub Desktop https://desktop.github.com/
5. Klona Warnicke/Kandidatarbete-Chalmers-MCCX02-19-06 från GitHub, alternativt från länken https://github.com/Warnicke/Kandidatarbete-Chalmers-MCCX02-19-06/ till en lämplig mapp på datorn. I GitHub Desktop kan man öppna filerna direkt i Visual Studio Code.
6. (Valfritt) Ladda ner PyCharm https://www.jetbrains.com/pycharm/ PyCharm har mer avancerade funktioner för att skriva kod i Python.

#### Vad är Git och GitHub?
Git är ett versionshanteringsprogram som i huvudsak är byggd för att hantera projekt med öppen källkod. Vanliga synkroniseringsprogram, t.ex. Google Drive, OneDrive, DropBox och ShareLaTex fungerar bra om man skriver i ett gemensammt textdokument eller delar filer som inte ändras så ofta. Ett ShareLaTex-dokument kan kompileras även om någon fortfarande skriver och inte är färdig med texten. Däremot är det inte säkert att det går att kompilera ett Java-program eller ett Pyton-program om flera personer ändrar samtidigt i filen. Innan en person programmerat klart sin del kan det finnas massa error och fel som gör att kompilatorn inte kan köra. Det är då som ett versionshanteringsprogram kommer till användning. 

Versionshantering ett system för att bokföra olika versioner av en fil. Det innebär att alla deltagare i ett projekt har en egen lokal verison av alla filer i projektet. När en deltagare ändrar en fil ändras filen endast i den lokala versionen. När deltagaren är färdig med sina ändringar i den lokala versionen kan den lokala versionen sammanfogas med den ursprungliga versionen. På så sätt kan alla deltagare i lugn och ro programmera på sina skilda delar och i slutändan sammanfoga allt när delarna är färdiga. 

Git fungerar på många sätt väldigt bra som versionshanteringsprogam, det enda problemet är att Git är kommandoradsbaserat vilket innebär att all hantering av verisoner sker med kommandon i kommandotolken/terminalen. GitHub är ett grafiskt system för verisonhantering som bygger på Git. GitHub lagrar också en orginalversion av projektet online med öppen källkod som är tillgänglig för alla att ladda ner till en lokal version. Det är sedan orginalversionen online som alla lokala versioner sammanfogas med. 

#### Ordlista

**`Repository`** = datakatalog (alt. versionsarkiv, projektförråd, eller repositorium) 
är det som normalt ses som själva projektet och alla filer som är kopplade till projektet. Förväxla inte med det som GitHub kallar för Projects.

**`Branch`** = gren är en version av projektet. Två grenar kan utvecklas åt olika ritkningar var för sig för att sedan sammanfogas. En gren kan både finnas som en lokal version på datorn och online på GitHub. 

**`Local branch`** = lokal gren, den gren som sparas lokalt på datorn.

**`Remote branch`** eller **`origin`** = gren som sparas online på GitHub. Lokala grenar sammanfogas med Remote/origin-grenen utan att påverka orginalgrenen (*master*).

**`master`** = orginalgrenen, den gren som alla andra grenar så småningom kommer sammanfogas med.

**`Merge`** = sammanfoga innehållet i en gren till en annan.

**`Rebase`** = också sammanfoga, men på ett annat (okänt) sätt.

**`Checkout`** = byta gren.

**`Commit`** = sammanställer (bokför) alla ändringar av en lokal gren och lagrar ändringarna som ett paket på datorn. För att committa måsten en lämplig kommentar skrivas för att kort beskriva vad som ändrats. Notera att Commit *inte* sammanfogar grenen med onlineversionen (Remote/origin) på GitHub. För att göra detta måste grenen *pushas*. 

**`Push`** = sammanfogar alla commits av en gren med onlineversionen (Remote/origin) på GitHub. Om det finns ändringar i koden på precis samma ställe som olika personer gjort uppstår en så kallas *merge conflict*. 

**`Merge conflict`** = konflikt vid sammanfogning av två grenar. Då måste man välja vilken kod som ska användas i den del av koden som konflikten uppstår. Det går även att blanda koden eller skriva ny kod i de konfliktdrabbade delarna. 

**`Pull`** = hämta Remote/origin grenen från GitHub och sammanfoga den med den lokala grenen. 

**`Pull requests`** = om det uppstår en *merge conflict* och man själv inte vet vilken ändring som är bäst kan man välja att göra en pull request från Remote/origin. Det innebär att en annan person får avgöra hur sammanfogningen ska gå till. Detta görs i GitHub under fliken *Pull requests* (tredje fliken till vänster).

**`Revert`** = återkalla en ändring. Om en ändring inte var bra kan den helt enkelt återkallas och så blir allt som förut. 
