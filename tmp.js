
let serial = require("serial");
serial.setup("usart", 115200);
serial.write("info\r\n");
for (let i = 0; i < 40; i++) {
    let data = serial.readAny(300);
    if (data) print(data);
}
serial.end();
