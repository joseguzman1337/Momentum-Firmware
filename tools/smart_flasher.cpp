#include <iostream>
#include <vector>
#include <string>
#include <iomanip>
#include <thread>
#include <chrono>
#include <cstring>
#include <stdexcept>
#include <cstdlib>
#include <ctime>

// --- 0. CROSS-PLATFORM SERIAL PORT WRAPPER ---
#ifdef _WIN32
    #include <windows.h>
#else
    #include <fcntl.h>
    #include <termios.h>
    #include <unistd.h>
    #include <errno.h>
#endif

class SimpleSerial {
private:
#ifdef _WIN32
    HANDLE hSerial;
#else
    int serial_fd;
#endif
    std::string port_name;
    bool connected;

public:
    SimpleSerial(std::string port, unsigned int baud_rate) : port_name(port), connected(false) {
#ifdef _WIN32
        // --- WINDOWS IMPLEMENTATION ---
        hSerial = CreateFile(port.c_str(), GENERIC_READ | GENERIC_WRITE, 0, 0, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, 0);
        if (hSerial == INVALID_HANDLE_VALUE) throw std::runtime_error("Error opening port");

        DCB dcbSerialParams = {0};
        dcbSerialParams.DCBlength = sizeof(dcbSerialParams);
        if (!GetCommState(hSerial, &dcbSerialParams)) throw std::runtime_error("Error getting state");

        dcbSerialParams.BaudRate = baud_rate;
        dcbSerialParams.ByteSize = 8;
        dcbSerialParams.StopBits = ONESTOPBIT;
        dcbSerialParams.Parity = NOPARITY;
        if (!SetCommState(hSerial, &dcbSerialParams)) throw std::runtime_error("Error setting state");

        // Set timeouts
        COMMTIMEOUTS timeouts = {0};
        timeouts.ReadIntervalTimeout = 50;
        timeouts.ReadTotalTimeoutConstant = 50;
        timeouts.ReadTotalTimeoutMultiplier = 10;
        timeouts.WriteTotalTimeoutConstant = 50;
        timeouts.WriteTotalTimeoutMultiplier = 10;
        SetCommTimeouts(hSerial, &timeouts);
#else
        // --- LINUX / MACOS IMPLEMENTATION ---
        serial_fd = open(port.c_str(), O_RDWR | O_NOCTTY | O_SYNC);
        if (serial_fd < 0) throw std::runtime_error("Error opening port: " + std::string(strerror(errno)));

        struct termios tty;
        if (tcgetattr(serial_fd, &tty) != 0) throw std::runtime_error("Error from tcgetattr");

        // Map common baud rates (default 115200 if unsupported)
        speed_t speed = B115200;
        switch(baud_rate) {
            case 9600: speed = B9600; break;
            case 19200: speed = B19200; break;
            case 38400: speed = B38400; break;
            case 57600: speed = B57600; break;
            case 115200: default: speed = B115200; break;
        }

        cfsetospeed(&tty, speed);
        cfsetispeed(&tty, speed);

        tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8-bit chars
        tty.c_iflag &= ~IGNBRK;
        tty.c_lflag = 0;
        tty.c_oflag = 0;
        tty.c_cc[VMIN]  = 0;
        tty.c_cc[VTIME] = 5; // 0.5 seconds read timeout

        tty.c_iflag &= ~(IXON | IXOFF | IXANY);
        tty.c_cflag |= (CLOCAL | CREAD);
        tty.c_cflag &= ~(PARENB | PARODD);
        tty.c_cflag &= ~CSTOPB;
        tty.c_cflag &= ~CRTSCTS;

        if (tcsetattr(serial_fd, TCSANOW, &tty) != 0) throw std::runtime_error("Error from tcsetattr");
#endif
        connected = true;
    }

    ~SimpleSerial() {
        if (connected) {
#ifdef _WIN32
            CloseHandle(hSerial);
#else
            close(serial_fd);
#endif
        }
    }

    void write_data(const std::vector<uint8_t>& data) {
#ifdef _WIN32
        DWORD bytes_written;
        if (!WriteFile(hSerial, data.data(), (DWORD)data.size(), &bytes_written, NULL) || bytes_written != data.size())
            throw std::runtime_error("Write error");
#else
        ssize_t res = write(serial_fd, data.data(), data.size());
        if (res < 0 || (size_t)res != data.size())
            throw std::runtime_error("Write error");
#endif
    }

    void read_data(std::vector<uint8_t>& buffer, size_t size) {
        buffer.resize(size);
        size_t received = 0;
        while (received < size) {
#ifdef _WIN32
            DWORD bytes_read = 0;
            if (!ReadFile(hSerial, buffer.data() + received, (DWORD)(size - received), &bytes_read, NULL))
                throw std::runtime_error("Read error");
#else
            ssize_t bytes_read = read(serial_fd, buffer.data() + received, size - received);
            if (bytes_read < 0)
                throw std::runtime_error("Read error");
#endif
            if (bytes_read == 0) break; // Timeout
            received += (size_t)bytes_read;
        }
        buffer.resize(received);
    }
};

// --- 1. AESTHETICS ---
namespace Style {
    const std::string RST = "\033[0m";
    const std::string BOLD = "\033[1m";
    const std::string RED = "\033[31m";
    const std::string GRN = "\033[32m";
    const std::string YEL = "\033[33m";
    const std::string CYN = "\033[36m";
    const std::string GRY = "\033[90m";

    void draw_progress(float pct, const std::string& label) {
        int width = 25;
        int pos = (int)(width * pct);
        std::cout << "\r  " << CYN << "[";
        for (int i = 0; i < width; ++i) {
            if (i < pos) std::cout << "=";
            else if (i == pos) std::cout << ">";
            else std::cout << "-";
        }
        std::cout << "] " << BOLD << (int)(pct * 100.0f) << "% " << RST << GRY << label << RST << "\033[K" << std::flush;
    }

    void print_badge(const std::string& color, const std::string& text, const std::string& msg) {
        std::cout << color << BOLD << " " << text << " " << RST << " " << msg << "\n";
    }
}

// --- 2. Abstract Flash Interface ---
class IFlashHardware {
public:
    virtual ~IFlashHardware() {}
    virtual void read_sector(size_t index, std::vector<uint8_t>& buffer) = 0;
    virtual void erase_sector(size_t index) = 0;
    virtual void write_sector(size_t index, const std::vector<uint8_t>& data) = 0;
    virtual size_t get_sector_size() const = 0;
    virtual size_t get_total_size() const = 0;
};

// --- 3. Serial-backed Hardware Implementation (example protocol) ---
class SerialHardware : public IFlashHardware {
    SimpleSerial* serial;
    const uint8_t CMD_READ  = 0x10;
    const uint8_t CMD_ERASE = 0x20;
    const uint8_t CMD_WRITE = 0x30;
    const size_t SECTOR_SIZE = 4096;
    const size_t TOTAL_SIZE  = 65536;

public:
    explicit SerialHardware(SimpleSerial* s) : serial(s) {}

    size_t get_sector_size() const override { return SECTOR_SIZE; }
    size_t get_total_size()  const override { return TOTAL_SIZE; }

    void read_sector(size_t index, std::vector<uint8_t>& buffer) override {
        std::vector<uint8_t> cmd = {CMD_READ, (uint8_t)index};
        serial->write_data(cmd);
        buffer.resize(SECTOR_SIZE);
        serial->read_data(buffer, SECTOR_SIZE);
    }

    void erase_sector(size_t index) override {
        std::vector<uint8_t> cmd = {CMD_ERASE, (uint8_t)index};
        serial->write_data(cmd);
        std::vector<uint8_t> ack;
        serial->read_data(ack, 1);
        // TODO: check ack[0] in real implementation
    }

    void write_sector(size_t index, const std::vector<uint8_t>& data) override {
        if(data.size() != SECTOR_SIZE) throw std::runtime_error("write_sector: invalid data size");
        std::vector<uint8_t> cmd = {CMD_WRITE, (uint8_t)index};
        serial->write_data(cmd);
        serial->write_data(data);
        std::vector<uint8_t> ack;
        serial->read_data(ack, 1);
    }
};

// --- 4. SmartFlasher Logic ---
class SmartFlasher {
    IFlashHardware* hw;

public:
    explicit SmartFlasher(IFlashHardware* hardware) : hw(hardware) {}

    bool sync(const std::vector<uint8_t>& new_fw) {
        size_t sector_sz = hw->get_sector_size();
        size_t total_sz  = hw->get_total_size();
        size_t num_sectors = total_sz / sector_sz;

        if(new_fw.size() != total_sz) {
            Style::print_badge(Style::RED, "ERR", "Firmware size mismatch");
            return false;
        }

        std::cout << "\n" << Style::BOLD << "⚡ HARDWARE LINK ACTIVE" << Style::RST << "\n";

        // Analysis phase
        std::vector<bool> dirty(num_sectors, false);
        std::vector<uint8_t> dev_buf(sector_sz);
        size_t dirty_count = 0;

        for(size_t i = 0; i < num_sectors; ++i) {
            Style::draw_progress((float)i / (float)num_sectors, "Analyzing sectors...");
            hw->read_sector(i, dev_buf);
            if(std::memcmp(dev_buf.data(), &new_fw[i * sector_sz], sector_sz) != 0) {
                dirty[i] = true;
                dirty_count++;
            }
        }
        Style::draw_progress(1.0f, "Analysis complete.");
        std::cout << "\n\n";

        if(dirty_count == 0) {
            Style::print_badge(Style::GRN, "✓ SYNCED", "Firmware is already up to date.");
            return true;
        }

        // Flashing phase
        std::cout << Style::BOLD << "   SYNCING " << dirty_count << " SECTORS:" << Style::RST << "\n";
        for(size_t i = 0; i < num_sectors; ++i) {
            if(!dirty[i]) continue;

            std::cout << Style::GRY << "   ├─ Sector " << std::setw(2) << std::setfill('0') << i << ": " << Style::RST;
            std::cout << Style::YEL << "Erase..." << Style::RST << std::flush;

            hw->erase_sector(i);

            std::cout << "\b\b\b\b\b\b\b\b" << Style::CYN << "Write..." << Style::RST << std::flush;

            std::vector<uint8_t> chunk(new_fw.begin() + i * sector_sz, new_fw.begin() + (i + 1) * sector_sz);
            hw->write_sector(i, chunk);

            std::cout << "\b\b\b\b\b\b\b\b" << Style::GRN << "Updated " << Style::RST << "\n";
        }

        std::cout << "\n";
        Style::print_badge(Style::GRN, "✓ DONE", "Device successfully synchronized.");
        return true;
    }
};

// --- 5. main ---
int main(int argc, char* argv[]) {
    std::srand((unsigned)std::time(nullptr));

    std::string port;
#ifdef _WIN32
    port = "COM3";
#elif __APPLE__
    port = "/dev/cu.usbserial-0001";
#else
    port = "/dev/ttyUSB0";
#endif

    if(argc > 1) port = argv[1];

    std::cout << "Targeting port: " << port << "\n";

    try {
        SimpleSerial serial(port, 115200);
        SerialHardware hw(&serial);

        // Example firmware buffer
        std::vector<uint8_t> firmware(hw.get_total_size());
        for(auto& b : firmware) b = (uint8_t)(std::rand() % 255);

        SmartFlasher flasher(&hw);
        flasher.sync(firmware);
    } catch(const std::exception& e) {
        std::cerr << "\n" << Style::RED << "  ┃ ERROR: " << e.what() << Style::RST << "\n";
        std::cerr << Style::RED << "  ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" << Style::RST << "\n";
        return 1;
    }

    return 0;
}
