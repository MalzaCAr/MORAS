# IDEJA
# 1. Iz asemblerske datoteke izbaciti sve razmake i komentare. Sjetite
#    se kako komentari u hack asembleru mogu biti jednolinijski i
#    viselinijski.
# 2. Sve simbole i varijable pretvoriti u numericke adrese (brojevi
#    linija ili adrese u memoriji).
# 3. Parsirati naredbe (A i C-instrukcije).



class Parser:
    #from parseLines import _parse_lines, _parse_line
    #from parseComms import _parse_commands, _parse_command, _init_comms
    #from parseSymbs import _parse_symbols, _parse_labels, _parse_variables, _init_symbols
    #from parseMacro import _parse_macros, _parse_macro
    
    def _parse_lines(self):
        self._comment = False    
        self._iter_lines(self._parse_line)

    def _parse_line(self, line, p, o):
        l = ""
        i = 0
        while i < len(line) - 1:
            p = line[i] + line[i + 1]

            if (self._comment == False and p == "/*") or (self._comment and p == "*/"):
                self._comment = not self._comment
                i += 1
            elif self._comment == False and p == "*/":
                self._flag = False
                self._line = o
                self._errm = "Unbalanced comment delimiter"
            elif (p == "//"):
                break
            elif line[i].isspace() == False and self._comment == False:
                l += line[i]

            i += 1
        return l 

    def _parse_commands(self):
        self._init_comms()
        self._iter_lines(self._parse_command)

    # Ukoliko instrukcija pocinje s "@", ona je A-instrukcija te broj koji dolazi
    # nakon nje pretvaramo u 15-bitni binarni broj kojemu na pocetak dodamo jednu
    # nulu. Npr. "@17" pretvaramo u "0000000000010001".
    #
    # U suprotnom smo naisli na C-instrukciju koja je oblika
    #   "dest = comp; jmp".
    # Pri tome je jedini nuzan dio instrukcije "comp".
    #
    # Dekodiranje vrsimo koristeci se rjecnicima inicijaliziranima u funkciji
    # "_init_comms". Konacni oblik instrukcije je
    #   "1 1 1 a c1 c2 c3 c4 c5 c6 d1 d2 d3 j1 j2 j3".
    def _parse_command(self, line, b, c):
        if line.startswith('@'):
            num = int(line[1:])
            if (num < 0 or num > 32767):
                self._flag = False
                self._line = c
                self._errm = "Error: address too big (max. 32767)"
                return
            return "{0:016b}".format(num)
        
        else:
            dest = ""
            op = ""
            jmp = ""
            
            l = line.split("=")
            if len(l) > 1:
                dest = l[0]
                l = l[1]
            else:
                l = l[0]
            
            l = l.split(";")
            if len(l) > 1:
                op = l[0]
                jmp = l[1]
            else:
                op = l[0]
            
            if op in self._op:
                op = self._op[op]
            else:
                self._flag = False
                self._line = c
                self._errm = "Invalid operation: " + op
            
            if dest in self._dest:
                dest = self._dest[dest]
            else:
                self._flag = False
                self._line = c
                self._errm = "Invalid destination: " + dest
            
            if jmp in self._jmp:
                jmp = self._jmp[jmp]
            else:
                self._flag = False
                self._line = c
                self._errm = "Invalid jump: " + jmp
                
            return "111" + op + dest + jmp

    # Inicijalizacija C-instrukcija.
    def _init_comms(self):
        self._op = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "A+D": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "A&D": "0000000",
            "D|A": "0010101",
            "A|D": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "M+D": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "M&D": "1000000",
            "D|M": "1010101",
            "M|D": "1010101"
        }
        self._jmp = {
            "" : "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }
        self._dest = {
            "" : "000",
            "M" : "001",
            "D" : "010",
            "MD" : "011",
            "A" : "100",
            "AM" : "101",
            "AD" : "110",
            "AMD" : "111"
        }

    def _parse_symbols(self):
        # Inicijalizacija predefiniranih oznaka.
        self._init_symbols()
        
        self._variables = {}
        self._num_vars = 16
        
        self._iter_lines(self._parse_labels)
        self._iter_lines(self._parse_variables)

    # Svaka oznaka mora biti sadrzana unutar oblih zagrada. Npr. "(LOOP)". Svaka
    # oznaka koju procitamo treba zapamtiti broj linije u kojoj se nalazi i biti
    # izbrisana iz nje. Koristimo dictionary _labels.
    def _parse_labels(self, line, p, o):
        if line.startswith('(') and line.endswith(')'):
            label = line[1:-1]  #dohvatimo oznaku izmđeu zagrada
            if len(label) == 0:
                self._flag = False
                self._line = o
                self._errm = "Invalid label"
            else:
                self._labels[label] = str(p)
            
            return ""
        
        else:
            return line

    # Svaki poziv na varijablu ili oznaku je oblika "@NAZIV", gdje naziv nije broj.
    # Prvo provjeriti oznake ("_labels"), a potom varijable ("_vars"). Varijablama
    # dodjeljujemo memorijske adrese pocevsi od 16. Ova funkcija nikad ne vraca
    # prazan string!
    def _parse_variables(self, line, p, o):
        if not line.startswith('@'):
            return line
        
        l = line[1:]
        
        if l[0] == '-':
            self._flag = False
            self._line = o
            self._errm = "Address can not be a negative number!"
            return
        
        if l.isdigit():
            return line
        
        if l in self._labels:
            return '@' + self._labels[l]
        
        if l not in self._variables:
            self._variables[l] = str(self._num_vars)
            self._num_vars += 1
        
        return '@' + self._variables[l]

    # Inicijalizacija predefiniranih oznaka.
    def _init_symbols(self):
        self._labels = {
            "SCREEN" : "16384",
            "KBD" : "24576",
            "SP" : "0",
            "LCL" : "1",
            "ARG" : "2",
            "THIS" : "3",
            "THAT" : "4"
        }
        
        for i in range(0, 16):
            self._labels["R" + str(i)] = str(i)

    def _parse_macros(self):
        self._counter = 0
        self._stack = []
        self._iter_lines(self._parse_macro)

    def _parse_macro(self, line, p, o):
        if line[0] == '$':
            if line[1] + line[2] == "MV":
                A = line[4]
                B = line[6]
                l = "@" + A + "\nD=M\n@" + B + "\nM=D\n"
            
            elif line[1] + line[2] + line[3] == "SWP":
                A = line[5]
                B = line[7]
                l = "@" + A + "\nD=M\n"
                l += "@15\nM=D\n@" + B + "\nD=M\n"
                l += "@" + A + "\nM=D\n@15\nD=M\n@" + B + "\nM=D\n"
            
            elif line[1] + line[2] + line[3] == "ADD":
                A = line[5]
                B = line[7]
                D = line[9]
                l = "@" + A + "\nD=M\n@" + B + "\nD=D+M\n@" + D + "\nM=D\n"
            
            elif (len(line)>=5):
                if line[1] + line[2] + line[3] + line[4] + line[5] == "WHILE":
                    self._counter += 1
                    self._stack.append(self._counter)
                    A = line[7]
                    l = "(WHILE" + str(self._counter) + ")"
                    l += "\n@" + A + "\nD=M\n"
                    l += "@END" + str(self._counter)
                    l += "\nD;JEQ\n"
            
            elif line[1] + line[2] + line[3] == "END":
                n = self._stack.pop()
                l = "@WHILE" + str(n) + "\n0;JMP\n"
                l += "(END" + str(n) + ")\n"
            
            else:
                self._flag = False
                self._line = o
                self._errm = "Error: invalid macro name."
            
            return l
        
        return line
        

    def __init__(self, filename):
        # Otvaramo input asemblersku datoteku.
        try:
            #jer sam na linuxu, moram ovako otvoriti file. za testiranje koristite liniju ispod ove.
            self._file = open("/home/fran/coding_projects/MORAS/zadaca_3/" + filename + ".asm", "r")
            #self._file = open(filename + ".asm", "r")
        except:
            Parser._error("File", -1, "Cannot open source file")
            return

        # Linije iz input datoteke upisujuemo u ovu listu.
        self._lines = []
        
        # Citamo input datoteku.
        try:
            self._read_lines()
        except:
            Parser._error("File", -1, "Cannot read source file.")
            return

        # Pogreske prilikom parsiranja.
        self._flag = True # Ukoliko je flag postavljen na False, parsiranje je neuspjesno.
        self._line = -1   # lokacija (broj linije) na kojoj se pogreska nalazi.
        self._errm = ""   # Poruka koja opisuje pogresku.

        # Parsiramo linije izvornog koda.
        self._parse_lines()
        if self._flag == False:
            Parser._error("PL", self._line, self._errm)
            return
        
        #Parsiramo makro 
        self._parse_macros()
        if self._flag == False:
            Parser._error("PL", self._line, self._errm)
            return
        
        #Parsiramo simbole iz koda
        self._parse_symbols()
        if self._flag == False:
            Parser._error("SYM", self._line, self._errm)
            return
        
        self._parse_commands()
        if self._flag == False:
            Parser._error("COM", self._line, self._errm)
            return
            
        # Na kraju parsiranja strojni kod upisujemo u ".hack" datoteku.
        try:
            self._outfile = open(filename + ".hack", "w")
        except:
            Parser._error("File", -1, "Cannot open output file")
            return

        try:
            self._write_file()
        except:
            Parser._error("File", -1, "Cannot write to output file")
            return          

    # Funkcija koja cita input datoteku te svaki redak sprema u listu uredjenih
    # trojki kojima su koordinate
    #   1. originalna linija iz datoteke
    #   2. broj linije u parsiranoj datoteci (u pocetku isti kao 3.)
    #   3. broj linije u originalnoj datoteci
    def _read_lines(self):
        n = 0
        for line in self._file:
            self._lines.append((line + "\n", n, n))
            n += 1

    # Funkcija upisuje parsirane linije u output ".hack" datoteku.
    def _write_file(self):
        for (line, p, o) in self._lines:
            self._outfile.write(line)
            if (line[-1] != "\n"):
                self._outfile.write("\n")

    # Funkcija iterira procitanim linijama i na svaku primjenjuje funkciju
    # "func". Funkcija "func" vraća string koji odgovara vrijednosti parsirane
    # linije.
    #
    # Primjer:
    # ("@END", 4, 4) postaje ("@3", 3, 4)
    #
    # Ukoliko je duljina vracene linije 0, tu liniju brisemo. Takodjer, svaka
    # funkcija "func" mora se brinuti o pogreskama na koje moze naici (npr.
    # viselinijski komentari koji nisu zatvoreni ili pogresna naredba M=B+1).
    def _iter_lines(self, func):
        newlines = []
        i = 0
        for (line, p, o) in self._lines:
            newline = func(line, i, o)
            if (self._flag == False):
                break
            if (len(newline) > 0):
                if "\n" in newline:
                    for part in newline.split(): 
                        if part != '':
                            newlines.append((part, i, o))
                            i += 1
                else:
                    newlines.append((newline, i, o))
                    i += 1
        self._lines = newlines
        
    @staticmethod
    def _error(src, line, msg):
        if len(src) > 0 and line > -1:
            print("[" + src + ", " + str(line) + "] " + msg)
        elif len(src) > 0:
            print("[" + src + "] " + msg)
        else:
            print(msg)  


if __name__ == "__main__":
    #Parser("test")
    Parser("zad3a")
    Parser("zad3b")
