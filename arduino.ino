#include <LiquidCrystal.h>

// Pokretanje LCD ekrana (RS, EN, D4, D5, D6, D7)
LiquidCrystal lcd(12, 11, 5, 4, 3, 2);

const int alarmPiezo = 8; // Alarm za kad je vozac pospan
const int crveniLED = 6; // Lampica kada je vozac pospan
const int zeleniLED = 7; // Lampica kada je vozac budan

String inputString = ""; // Pamti serial input koji salje Python skripta

void setup() {
  lcd.begin(16, 2); // 16x2 LCD
  Serial.begin(9600); // Port na slusa za informacije

  // Postavljanje pinova na output za lampice i piezo
  pinMode(crveniLED, OUTPUT);
  pinMode(zeleniLED, OUTPUT);
  pinMode(alarmPiezo, OUTPUT);

  lcd.print("Upalite kameru!"); // Defaultna poruka koja stoji prije nego sto se skripa upali ili se prepozna lice
  digitalWrite(zeleniLED, HIGH); // Pali zelenu lampicu
  digitalWrite(crveniLED, LOW); // Ostavlja crvenu lampicu ugasenom
}

void loop() {
  // Slusa da li je na portu ista dostupno
  if (Serial.available()) {
    inputString = Serial.readStringUntil('\n'); // Cita string

    inputString.trim(); // Brise prazna mjesta u stringu

    // Ukoliko je vozac pospan
    if (inputString == "pospan") {
      lcd.clear(); // Brise sta pise na ekranu trenutno
      lcd.print("Vozac je pospan!"); // Poruka korisniku / vozacu
      digitalWrite(zeleniLED, LOW); // Gasi zelenu lampicu
      pospaniAlarm(); // Pokrece funkciju da razbudi vozaca
    }
    // Ukoliko je vozac budan
    else if (inputString == "budan") {
      lcd.clear(); // Brise sta pise na ekranu trenutno
      lcd.print("Vozac je budan!"); // Poruka korisniku / vozacu
      digitalWrite(zeleniLED, HIGH); // Pokrece zelenu lampicu
      digitalWrite(crveniLED, LOW); //Gasi crvenu lampicu
    }
  }
}

void pospaniAlarm() {
  while(true) {
    // Ovaj dio je za blinkanje crvene lamice i alarma koji treba razbuditi vozaca
    digitalWrite(alarmPiezo, HIGH); // Proizvodi zvuk da razbudi vozaca
    digitalWrite(crveniLED, HIGH); // Pali lampicu
    delay(300); // Ceka 300ms
    digitalWrite(alarmPiezo, LOW); // Gasi zvuk
    digitalWrite(crveniLED, LOW); // Gasi lampcu
    delay(300); // Ceka 30ms ponovo

    // Isto kao ranije
    if (Serial.available()) {
    inputString = Serial.readStringUntil('\n');

    inputString.trim();

    // Ovo ce se pokrenuti ako se deketuje da se vozac probudio
    if (inputString == "budan") break;
    }
  }
  // Isto kao ranije
  lcd.clear();
  lcd.print("Vozac je budan!");
  digitalWrite(zeleniLED, HIGH);
  digitalWrite(crveniLED, LOW);
}
