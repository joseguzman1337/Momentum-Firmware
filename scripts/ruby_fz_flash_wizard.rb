#!/usr/bin/env ruby
# Fast Ruby wizard for Flipper Zero / WiFi devboard flashing.

require 'optparse'
require 'time'

ROOT = File.expand_path('..', __dir__)
FBT = File.join(ROOT, 'fbt')

unless File.executable?(FBT)
  warn "Error: fbt not found or not executable at #{FBT}"
  exit 1
end

options = {
  mode: :interactive,
  timeout: 180,
  interval: 0.1,
  port: nil
}

OptionParser.new do |opts|
  opts.banner = 'Usage: ruby_fz_flash_wizard.rb [options]'

  opts.on('--smart-flash', 'Run fbt smart_flash (recommended)') { options[:mode] = :smart_flash }
  opts.on('--flash-usb-full', 'Run fbt flash_usb_full') { options[:mode] = :flash_usb_full }
  opts.on('--flash-usb', 'Run fbt flash_usb') { options[:mode] = :flash_usb }
  opts.on('--devboard-flash', 'Run fbt devboard_flash now') { options[:mode] = :devboard_flash }
  opts.on('--devboard-fast', 'Wait for ESP (VID 303a) then flash devboard') { options[:mode] = :devboard_fast }
  opts.on('--port PORT', 'Set PORT=/dev/ttyACMx for flash_usb* modes') { |v| options[:port] = v }
  opts.on('--timeout SECONDS', Integer, 'Timeout for wait-based modes (default: 180)') { |v| options[:timeout] = v }
  opts.on('--interval SECONDS', Float, 'Polling interval for wait-based modes (default: 0.1)') { |v| options[:interval] = v }
  opts.on('-h', '--help', 'Show help') do
    puts opts
    exit 0
  end
end.parse!

def run_cmd(cmd, env = {})
  printable_env = env.map { |k, v| "#{k}=#{v}" }.join(' ')
  puts "\n$ #{printable_env} #{cmd}".strip
  ok = system(env, cmd, chdir: ROOT)
  exit(ok ? 0 : 1) if ok == false || ok.nil?
end

def tty_ports
  (Dir.glob('/dev/ttyACM*') + Dir.glob('/dev/ttyUSB*')).sort
end

def esp_bootloader_present?
  system('lsusb -d 303a: >/dev/null 2>&1')
end

def wait_for_esp(timeout:, interval:)
  start = Time.now
  while (Time.now - start) < timeout
    return true if esp_bootloader_present?
    sleep interval
  end
  false
end

def maybe_port_env(port)
  return {} if port.nil? || port.empty?
  { 'PORT' => port }
end

def run_mode(mode, options)
  case mode
  when :smart_flash
    run_cmd('./fbt smart_flash')
  when :flash_usb_full
    run_cmd('./fbt flash_usb_full', maybe_port_env(options[:port]))
  when :flash_usb
    run_cmd('./fbt flash_usb', maybe_port_env(options[:port]))
  when :devboard_flash
    run_cmd('./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"')
  when :devboard_fast
    puts "Waiting for ESP bootloader (VID 303a) for up to #{options[:timeout]}s..."
    unless wait_for_esp(timeout: options[:timeout], interval: options[:interval])
      warn 'Timeout: ESP bootloader not detected.'
      exit 1
    end
    puts 'ESP device detected. Flashing now...'
    run_cmd('./fbt devboard_flash ARGS="--wait --timeout 180 --auto-bootloader"')
  else
    raise "Unknown mode: #{mode}"
  end
end

def prompt(message)
  print message
  STDOUT.flush
  input = STDIN.gets
  exit 130 if input.nil?
  input.strip
end

def interactive_menu
  ports = tty_ports
  puts 'Fast FZ Flash Wizard (Ruby)'
  puts "Repo: #{ROOT}"
  puts
  puts 'Detected serial ports:'
  if ports.empty?
    puts '  (none)'
  else
    ports.each { |p| puts "  - #{p}" }
  end
  puts
  puts 'Select action:'
  puts '  1) smart_flash (recommended full flow)'
  puts '  2) flash_usb_full'
  puts '  3) flash_usb'
  puts '  4) devboard_flash (run now)'
  puts '  5) devboard_fast (wait for ESP bootloader, then flash)'
  puts '  q) quit'

  choice = prompt('Choice: ')
  case choice
  when '1'
    run_mode(:smart_flash, {})
  when '2', '3'
    default_port = ports.first.to_s
    selected = prompt("PORT value [#{default_port}]: ")
    selected = default_port if selected.empty?
    mode = choice == '2' ? :flash_usb_full : :flash_usb
    run_mode(mode, { port: selected })
  when '4'
    run_mode(:devboard_flash, {})
  when '5'
    timeout_str = prompt("Timeout seconds [180]: ")
    timeout = timeout_str.empty? ? 180 : timeout_str.to_i
    run_mode(:devboard_fast, { timeout: timeout, interval: 0.1 })
  when 'q', 'Q'
    puts 'Aborted.'
    exit 0
  else
    warn 'Invalid choice.'
    exit 1
  end
end

if options[:mode] == :interactive
  interactive_menu
else
  run_mode(options[:mode], options)
end
