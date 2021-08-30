def isint(string):
    try:
        int(string)
    except:
        return False
    return True


def get_char_only(string):
    s = ""
    for c in string:
        if 'a' <= c <= 'z' or 'A' <= c <= 'Z':
            s += c
    return s


def is_char_only(string):
    for c in string:
        if not ('a' <= c <= 'z' or 'A' <= c <= 'Z'):
            return False
    return True


def is_charblank_only(string):
    for c in string:
        if not ('a' <= c <= 'z' or 'A' <= c <= 'Z' or c == ' '):
            return False
    return True


def has_dash(string):
    for c in string:
        if not c == '-':
            return True
    return False


class Name:
    name2paper = {}

    def __init__(self, string, paper):
        list_ = string.strip().split(' ')
        self.words = []
        for t in list_:
            self.words.append(get_char_only(t))

        self.buaa = self.to_buaa()
        self.full = ' '.join(self.words)

        if paper is None:
            return
        if self.full in Name.name2paper:
            Name.name2paper[self.full].append(paper)
        else:
            Name.name2paper[self.full] = [paper]

    def to_buaa(self):
        s = self.words[-1]
        for t in self.words[:-1]:
            s += " " + t[0]
        return s


class Names:
    def __init__(self, string, paper):
        list_ = string.split(" and\n")
        self.names = []
        for t in list_:
            self.names.append(Name(t.strip(), paper))

        self.buaa = ''
        if len(self.names) <= 3:
            for t in self.names[:-1]:
                self.buaa += t.buaa + ', '
            self.buaa += self.names[-1].buaa + '. '
        else:
            for t in self.names[:3]:
                self.buaa += t.buaa + ', '
            self.buaa += 'et al. '


class Conference:
    def __init__(self, string):
        s = string
        for i in range(len(string)):
            if string[i] == ':':
                s = string[i + 1:]

        list_ = s.split(' ')
        self.list_ = []
        if list_[-1] == "Conference" and list_[-2] == "European":
            self.list_.append("European")
            self.list_.append("Conference")
            list_ = list_[:-2]

        for t in list_:
            t = t.strip()
            if not isint(t) and is_char_only(t) and len(t) > 0:
                self.list_.append(t)

    def get_abbr(self):
        s = ""
        for t in self.list_:
            if 'A' <= t[0] <= 'Z':
                s += t[0]
        return s

    def to_buaa(self):
        return " ".join(self.list_)


class BookTitle:
    def __init__(self, string):
        list_ = string.split(',')
        self.conference = Conference(list_[0].strip())

        self.abbr = None
        self.place = []

        for t in list_:
            t = t.strip()
            if t[0] == '{':
                self.abbr = t.split('}')[0][1:]
            elif is_charblank_only(t) and t not in ["Proceedings"]:
                self.place.append(t)
            elif isint(t):
                self.year = t
            elif has_dash(t):
                self.date = t

    def get_abbr(self):
        if self.abbr is not None:
            return " (" + self.abbr + ")"
        if self.conference.get_abbr() == "CCVPR":
            return " (CVPR)"
        if self.conference.get_abbr() == "ACNIPS":
            return " (NIPS)"
        if self.conference.get_abbr() in ["CVPR", "ECCV", "ICLR"]:
            return " (" + self.conference.get_abbr() + ")"
        return ""

    def first(self):
        return self.conference.to_buaa() + self.get_abbr() + "[C]. " + self.place[-1] + ": "


class Entry:
    def __init__(self, string):
        assert string.find("= {") > 0
        key, value = string.split("= {")
        self.key = key.strip()
        self.value = value.strip()


class Bib:
    def __init__(self, string):
        assert string[0] == "@"
        self.type = ""
        for c in string[1:]:
            if 'a' <= c <= 'z':
                self.type += c
            else:
                break

        for i in range(len(string)):
            if string[i] == ' ':
                string = string[i + 1:]
                break

        list_ = string.split("},")
        for t in list_:
            entry = Entry(t)
            if entry.key == "editor":
                self.editor = Names(entry.value, None)
            elif entry.key == 'author':
                author_names = entry.value
            elif entry.key in ["booktitle"]:
                self.__dict__[entry.key] = BookTitle(entry.value)
            else:
                self.__dict__[entry.key] = entry.value

        self.author = Names(author_names, self.get_titile())

    def get_attr(self, attr):
        if attr in self.__dict__.keys():
            s = ""
            list_ = self.__dict__[attr].split(" ")
            for t in list_[:-1]:
                if t[0] != "{":
                    s += t + " "
            s += list_[-1]
            return s
        if attr == "publisher" and self.booktitle.get_abbr() == "(NIPS)":
            return "Advances in Neural Information Processing Systems"
        return "Unknown"

    def get_pages(self):
        if "pages" in self.__dict__.keys():
            return "-".join(self.pages.split("--"))
        return "Unknown"

    def get_titile(self):
        s = ""
        for c in self.title:
            if c == ' ' and s[-1] == ' ':
                continue
            elif c != "\n":
                s += c
        return s

    def to_buaa_inproceeding(self):
        s = ""
        s += self.author.buaa
        s += self.get_titile() + "[A]. "
        s += self.booktitle.first()
        s += self.get_attr("publisher") + ", "
        s += self.year + ":"
        s += self.get_pages() + "."
        return s

    def get_number(self):
        if "number" in self.__dict__.keys():
            return "(" + self.number + ")"
        return ""

    def to_buaa_article(self):
        s = ""
        s += self.author.buaa
        s += self.get_titile() + "[J]. "
        s += self.get_attr("journal") + ", "
        s += self.year + ", "
        s += self.volume
        s += self.get_number()
        s += ":" + self.get_pages() + "."
        return s

    def to_buaa(self):
        if self.type == "inproceedings":
            return self.to_buaa_inproceeding()
        if self.type == "article":
            return self.to_buaa_article()
        raise Exception


if __name__ == "__main__":
    t = Bib('''@inproceedings{DBLP:conf/nips/PathakLDIE19,
  author    = {Deepak Pathak and
               Christopher Lu and
               Trevor Darrell and
               Phillip Isola and
               Alexei A. Efros},
  editor    = {Hanna M. Wallach and
               Hugo Larochelle and
               Alina Beygelzimer and
               Florence d'Alch{\'{e}}{-}Buc and
               Emily B. Fox and
               Roman Garnett},
  title     = {Learning to Control Self-Assembling Morphologies: {A} Study of Generalization
               via Modularity},
  booktitle = {Advances in Neural Information Processing Systems 32: Annual Conference
               on Neural Information Processing Systems 2019, NeurIPS 2019, 8-14
               December 2019, Vancouver, BC, Canada},
  pages     = {2292--2302},
  year      = {2019},
  url       = {http://papers.nips.cc/paper/8501-learning-to-control-self-assembling-morphologies-a-study-of-generalization-via-modularity},
  timestamp = {Fri, 06 Mar 2020 16:59:09 +0100},
  biburl    = {https://dblp.org/rec/conf/nips/PathakLDIE19.bib},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}''')
    print(t.to_buaa())
