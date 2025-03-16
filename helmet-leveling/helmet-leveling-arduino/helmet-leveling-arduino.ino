#include <Servo.h>

#define NUM_SERVOS 8  // Define number of servos

Servo servos[NUM_SERVOS];  // Array to store all servos
int servoPins[NUM_SERVOS] = {3, 5, 6, 9, 10, 11, 12, 13};  // Servo pin mapping
int angles[NUM_SERVOS] = {90, 90, 90, 90, 90, 90, 90, 90};  // Store last positions

int selectedServo = 0;  // Default to first servo

void setup() {
    Serial.begin(9600);
    for (int i = 0; i < NUM_SERVOS; i++) {
        servos[i].attach(servoPins[i]);  // Attach servos
        servos[i].write(angles[i]);  // Move to initial position (90°)
    }
    Serial.println("Enter '1' to '8' to select a servo. Use '+' or '-' to adjust angle. 'R' to reset all servos.");
}

void loop() {
    if (Serial.available()) {
        char command = Serial.read();

        // Select a servo (1-8)
        if (command >= '1' && command <= '8') {
            selectedServo = command - '1';  // Convert to array index (0-7)
            Serial.print("Switched to Servo ");
            Serial.println(selectedServo + 1);
        }
        // Increase angle
        else if (command == '+') {
            if (angles[selectedServo] < 180) {
                angles[selectedServo] += 5;
                servos[selectedServo].write(angles[selectedServo]);
            }
        }
        // Decrease angle
        else if (command == '-') {
            if (angles[selectedServo] > 0) {
                angles[selectedServo] -= 5;
                servos[selectedServo].write(angles[selectedServo]);
            }
        }
        // Reset all servos to 0°
        else if (command == 'R') {
            Serial.println("Resetting all servos to 0°");
            for (int i = 0; i < NUM_SERVOS; i++) {
                angles[i] = 90;
                servos[i].write(angles[i]);
            }
        }

        Serial.print("Servo ");
        Serial.print(selectedServo + 1);
        Serial.print(" Angle: ");
        Serial.println(angles[selectedServo]);
    }

    delay(50);
}
