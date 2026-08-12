import base64
import sys
import os
import argparse

# Esempi di utilizzo:
# python pwrshift.py "whoami /groups"
# python pwrshift.py -f comandi_da_convertire.txt -o comandi_convertiti.txt

class Style:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    CLEAR = '\033[K'

def powershell_encode(command):
    if not command or not command.strip():
        return None
    
    full_cmd = command.strip() 
    
    flags = "powershell -w hidden -nop -e"
    
    def get_b64(cmd_str):
        unicode_bytes = cmd_str.encode('utf-16-le')
        return base64.b64encode(unicode_bytes).decode('utf-8')

    b64_result = get_b64(full_cmd)

    while '=' in b64_result:
        full_cmd += ' '
        b64_result = get_b64(full_cmd)

    return f"{flags} {b64_result}"

def main():
    parser = argparse.ArgumentParser(description="PwrShift: MSF-Style PS Encoder")
    parser.add_argument("command", nargs='?', help="Comando singolo da codificare")
    parser.add_argument("-f", "--file", help="File con lista di comandi")
    parser.add_argument("-o", "--output", help="File di destinazione")
    parser.add_argument("-q", "--quiet", action="store_true", help="Output pulito (solo il risultato)")
    
    args = parser.parse_args()

    pipe_input = None
    if not sys.stdin.isatty():
        pipe_input = sys.stdin.read().splitlines()

    if not args.command and not args.file and not pipe_input:
        print(f"{Style.BLUE}PwrShift v1.1{Style.END} - Uso: {sys.argv[0]} \"comando\" o pipe")
        sys.exit(0)

    if not args.quiet:
        print(f"{Style.BOLD}{Style.BLUE}--- PwrShift Encoder ---{Style.END}")

    results = []

    raw_commands = []
    if args.command: raw_commands.append(args.command)
    if pipe_input: raw_commands.extend(pipe_input)
    if args.file and os.path.exists(args.file):
        with open(args.file, 'r') as f:
            raw_commands.extend(f.read().splitlines())

    for cmd in raw_commands:
        encoded = powershell_encode(cmd)
        if encoded:
            if args.quiet:
                print(encoded)
            else:
                print(f"{Style.GREEN}[+]{Style.END} {cmd[:30]}... -> {Style.YELLOW}{encoded}{Style.END}")
            results.append(encoded)

    if args.output and results:
        with open(args.output, 'w') as f_out:
            f_out.write("\n".join(results) + "\n")
        if not args.quiet:
            print(f"\n{Style.BOLD}Salvati {len(results)} comandi in: {args.output}{Style.END}")

if __name__ == "__main__":
    main()