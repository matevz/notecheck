import hashlib, os, subprocess

CACHE_DIR = "/tmp/notecheck/"
LILYPOND_CMD = "lilypond -dbackend=svg -o {filename} -dno-point-and-click -dpreview -"

def generate_svg(snippet: str) -> []:
    """returns svg preview of the given lilypond snippet
    If the svg doesn't exist yet in the cache dir, it generates it by running
    lilypond command; otherwise it reads it from the disk."""
    lilysrc = """\paper{
  indent=0\mm
  line-width=140\mm
  oddFooterMarkup=##f
  oddHeaderMarkup=##f
  bookTitleMarkup = ##f
  scoreTitleMarkup = ##f
}

#(set-global-staff-size 17)	
"""
    lilysrc += snippet

    if not os.path.exists(CACHE_DIR):
        os.mkdir(CACHE_DIR)

    filename = os.path.join(CACHE_DIR, hashlib.md5(lilysrc.encode('utf-8')).hexdigest()) + '.preview.svg'
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            return file.read()

    s = subprocess.Popen(LILYPOND_CMD.format(
        filename=filename[:-12]).split(' '), # trim ".preview.svg" extension
        stderr=subprocess.STDOUT,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        close_fds=True
    )
    out = s.communicate(lilysrc.encode('utf-8'))[0]

    with open(filename, 'r') as file:
        return file.read()
