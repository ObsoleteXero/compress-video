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


def calculate_bitrate(filesize: float, length: float) -> str:
    v_br = round(filesize * 1024 * 8 / length - 128)
    return str(v_br) + "k"


def x265():
    # TODO: x265
    return


def x264(filename: str, bitrate: str) -> None:
    pass_one = subprocess.Popen(
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

    while True:
        line = pass_one.stdout.readline().decode("utf8", errors="replace").strip()
        if line == "":
            print("First Pass: Complete")
            break
        if line.startswith('total_size='):
            progress = round(int(line.lstrip('total_size=')) / (int(sys.argv[2]) * 1048576) * 100, 2)
            print(f"First Pass: {progress}%", end='\r')

    pass_two = subprocess.Popen(
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
            "2",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-progress",
            "-",
            "-nostats",
            "-loglevel",
            "error",
            "compressed_" + filename,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    while True:
        line = pass_two.stdout.readline().decode("utf8", errors="replace").strip()
        if line == "":
            print("Second Pass: Complete")
            break
        if line.startswith('total_size='):
            progress = round(int(line.lstrip('total_size=')) / (int(sys.argv[2]) * 1048576) * 100, 2)
            print(f"Second Pass: {progress}\%", end='\r')



if __name__ == "__main__":
    main()