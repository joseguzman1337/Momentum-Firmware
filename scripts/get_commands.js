let serial = require("serial");
serial.setup("usart", 115200);
print("GETTING_COMMANDS_START");
serial.write("

help
");
for (let i = 0; i < 50; i++) {
    let data = serial.readAny(300);
    if (data) print(data);
}
serial.end();
print("GETTING_COMMANDS_END");
