import subprocess
import sys


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} input target_filesize(MB)")
        return

    # TODO: Check inputs
    length = get_length(sys.argv[1])
    # TODO: Filesize formats
    filesize = float(sys.argv[2])

    br = calculate_bitrate(filesize, length)
    x264(sys.argv[1], br)


def get_length(filename: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return float(result.stdout)


def calculate_bitrate(filesize: float, duration: float) -> str:
    v_br = round(filesize * 1024 * 8 / duration - 128)
    return str(v_br) + "k"


def x265():
    # TODO: x265
    return


def x264(filename: str, bitrate: str) -> None:
    pass_one = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            filename,
            "-c:v",
            "libx264",
            "-b:v",
            bitrate,
            "-pass",
            "1",
            "-an",
            "-f",
            "null",
            "NUL",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    pass_two = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-i",
            filename,
            "-c:v",
            "libx264",
            "-b:v",
            "1639k",
            "-pass",
            "2",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "compressed_" + filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    while True:
        line = pass_two.stdout.readline().decode("utf8", errors="replace").strip()
        if line == "" and pass_two.poll() is not None:
            break
        print(line)


if __name__ == "__main__":
    main()
