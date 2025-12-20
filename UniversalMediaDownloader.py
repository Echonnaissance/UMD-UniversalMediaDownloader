
"""
Universal Media Downloader
A command-line tool for downloading videos and audio from YouTube, Twitter/X, Instagram, TikTok, and other platforms supported by yt-dlp.

Usage:
	python UniversalMediaDownloader.py <URL> [options]
	python UniversalMediaDownloader.py --config config.json
"""
# --- migrated and renamed from YTMP3urlConverter.py ---
import subprocess
import os
import sys
import argparse
import logging
import json
import re
from pathlib import Path
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# ...existing code from YTMP3urlConverter.py, with all references to YTMP3urlConverter, YT2MP3, etc. replaced with UniversalMediaDownloader...


def find_executable(name: str, possible_paths: List[str]) -> Optional[str]:
    # Try absolute/relative path first
    if os.path.isabs(name) or os.path.sep in name:
        if os.path.exists(name) and os.access(name, os.X_OK):
            return name

    # Check provided candidate paths
    for p in possible_paths:
        candidate = p
        if not os.path.isabs(candidate):
            candidate = os.path.join(os.getcwd(), candidate)
        if os.path.exists(candidate) and os.access(candidate, os.X_OK):
            return candidate

    # Search in PATH
    paths = os.environ.get("PATH", "").split(os.pathsep)
    exts = [""]
    if os.name == "nt":
        pathext = os.environ.get("PATHEXT", ".EXE;.BAT;.CMD;.COM")
        exts = pathext.split(os.pathsep)
    """
    YouTube/Twitter Video Downloader
    A command-line tool for downloading videos from YouTube, Twitter/X, and other platforms supported by yt-dlp.

    Usage:
        python UniversalMediaDownloader.py <URL> [options]
        python UniversalMediaDownloader.py --config config.json
    """
    import subprocess
    import os
    import sys
    import argparse
    import logging
    import json
    import re
    from pathlib import Path
    from typing import Optional, List

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    def find_executable(name: str, possible_paths: List[str]) -> Optional[str]:
        """
        Find an executable in multiple possible locations.

        Args:
            name: Name of the executable (e.g., 'yt-dlp.exe', 'ffmpeg.exe')
            possible_paths: List of paths to check

        Returns:
            Path to executable if found, None otherwise
        """
        # Check each possible path
        for path in possible_paths:
            full_path = os.path.abspath(path)
            if os.path.exists(full_path):
                logger.info(f"Found {name} at: {full_path}")
                return full_path

        # Check system PATH
        if sys.platform == "win32":
            try:
                result = subprocess.run(
                    [name.replace('.exe', ''), '--version'],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Found {name} in system PATH")
                    return name.replace('.exe', '')
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
        else:  # Linux/macOS
            try:
                result = subprocess.run(
                    ['which', name.replace('.exe', '')],
                    capture_output=True,
                    text=True,
                    check=False
                )
                if result.returncode == 0 and result.stdout.strip():
                    found_path = result.stdout.strip()
                    logger.info(f"Found {name} at: {found_path}")
                    return found_path
            except FileNotFoundError:
                pass

        return None

    def find_ytdlp(script_dir: str, project_root: str) -> Optional[str]:
        """
        Find yt-dlp executable in common locations.

        Args:
            script_dir: Directory where this script is located
            project_root: Project root directory

        Returns:
            Path to yt-dlp executable or None if not found
        """
        executable_name = 'yt-dlp.exe' if sys.platform == 'win32' else 'yt-dlp'

        possible_paths = [
            os.path.join(script_dir, executable_name),
            os.path.join(project_root, executable_name),
            os.path.join(project_root, 'dist', executable_name),
            os.path.join(project_root, 'backend', executable_name),
        ]

        return find_executable(executable_name, possible_paths)

    def find_ffmpeg(script_dir: str, project_root: str) -> Optional[str]:
        """
        Find ffmpeg executable in common locations.

        Args:
            script_dir: Directory where this script is located
            project_root: Project root directory

        Returns:
            Path to ffmpeg executable or None if not found
        """
        executable_name = 'ffmpeg.exe' if sys.platform == 'win32' else 'ffmpeg'

        possible_paths = [
            os.path.join(script_dir, executable_name),
            os.path.join(project_root, executable_name),
            os.path.join(project_root, 'dist', executable_name),
            os.path.join(project_root, 'backend', executable_name),
        ]

        return find_executable(executable_name, possible_paths)

    def build_yt_dlp_command(url: str, output_dir: str, audio_only: bool = False, format_str: Optional[str] = None) -> List[str]:
        cmd = ['yt-dlp', url]
        if audio_only:
            cmd += ['-x', '--audio-format', 'mp3']
        if format_str:
            cmd += ['-f', format_str]
        cmd += ['-o', os.path.join(output_dir, '%(title)s.%(ext)s')]
        return cmd

    def main(argv: Optional[List[str]] = None) -> int:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..'))

        ytdlp_path = find_ytdlp(script_dir, project_root)
        ffmpeg_path = find_ffmpeg(script_dir, project_root)

        parser = argparse.ArgumentParser(
            description='Universal Media Downloader')
        parser.add_argument('url', nargs='?', help='URL to download')
        parser.add_argument(
            '--config', help='Path to config file', default=None)
        parser.add_argument('--audio-only', action='store_true',
                            help='Extract audio as MP3')
        parser.add_argument(
            '--format', help='Format string for yt-dlp', default=None)
        parser.add_argument(
            '--output', help='Output directory', default='Downloads')

        args = parser.parse_args(argv)

        # Load config if provided
        if args.config:
            try:
                with open(args.config, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                    logger.info('Loaded config from %s', args.config)
            except Exception as e:
                logger.error('Failed to load config: %s', e)
                return 2

        if not args.url:
            parser.print_help()
            return 1

        output_dir = os.path.abspath(args.output)
        os.makedirs(output_dir, exist_ok=True)

        cmd = build_yt_dlp_command(
            args.url, output_dir, audio_only=args.audio_only, format_str=args.format)

        # Prefer discovered executable if available
        if ytdlp_path:
            cmd[0] = ytdlp_path

        try:
            logger.info('Running: %s', ' '.join(cmd))
            proc = subprocess.run(cmd, check=False)
            return proc.returncode
        except FileNotFoundError:
            logger.error(
                'yt-dlp not found. Please install yt-dlp or place it in the project root.')
            return 3

    if __name__ == '__main__':
        sys.exit(main())
