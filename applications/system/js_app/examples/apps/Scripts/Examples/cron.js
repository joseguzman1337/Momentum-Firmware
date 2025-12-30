let eventLoop = require("event_loop");
let rtc = require("rtc");

let target = { hour: 8, minute: 30, second: 0 };
let lastRunDay = 0;

eventLoop.subscribe(eventLoop.timer("periodic", 1000), function (_sub, _item) {
    let now = rtc.getDateTime();
    if (now.hour !== target.hour || now.minute !== target.minute || now.second !== target.second) {
        return;
    }
    if (now.day === lastRunDay) {
        return;
    }

    lastRunDay = now.day;
    print("Cron job fired at ", now.hour, ":", now.minute, ":", now.second);
});

eventLoop.run();
