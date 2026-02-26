let serial = require("serial");
serial.setup("usart", 115200);
print("Probing Serial...");
serial.write("help\r\n");
for (let i = 0; i < 10; i++) {
    let data = serial.readAny(200);
    if (data) {
        print("Received: " + data);
    }
}
serial.end();
print("Done.");
