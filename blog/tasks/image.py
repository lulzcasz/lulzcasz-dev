import os

from blog.utils.image import download_to_temp, process_and_save_image
from celery import shared_task


@shared_task(bind=True)
def process_image(self, relative_path, section):
    directory = os.path.dirname(relative_path)

    with download_to_temp(relative_path) as input_path:
        if section == "cover":
            versions = [
                {"size": "raw", "ext": "webp", "w": 2400, "h": 1260, "q": "95"},
                {"size": "large", "ext": "jpg", "w": 1200, "h": 630, "q": "3"},
                {"size": "medium", "ext": "avif", "w": 960, "h": 504, "crf": "26"},
                {"size": "small", "ext": "avif", "w": 480, "h": 252, "crf": "32"},
            ]

            for config in versions:
                final_path = os.path.join(
                    directory, f"{config['size']}.{config['ext']}"
                )
                vf_scale_crop = f"scale={config['w']}:{config['h']}:force_original_aspect_ratio=increase,crop={config['w']}:{config['h']}"

                if config["ext"] == "jpg":
                    args = [
                        "-vf",
                        vf_scale_crop,
                        "-threads",
                        "2",
                        "-q:v",
                        config["q"],
                        "-pix_fmt",
                        "yuv420p",
                    ]
                elif config["ext"] == "webp":
                    args = [
                        "-vf",
                        vf_scale_crop,
                        "-threads",
                        "2",
                        "-c:v",
                        "libwebp",
                        "-q:v",
                        config["q"],
                        "-pix_fmt",
                        "yuv420p",
                    ]
                else:
                    args = [
                        "-vf",
                        vf_scale_crop,
                        "-threads",
                        "2",
                        "-c:v",
                        "libaom-av1",
                        "-still-picture",
                        "1",
                        "-crf",
                        config["crf"],
                        "-cpu-used",
                        "6",
                        "-pix_fmt",
                        "yuv420p",
                    ]

                process_and_save_image(input_path, final_path, args)

        elif section == "content_image":
            vf_raw = "scale='min(1920,iw)':-2"
            path_raw = os.path.join(directory, "raw.webp")

            args_raw = [
                "-vf",
                vf_raw,
                "-threads",
                "2",
                "-c:v",
                "libwebp",
                "-q:v",
                "95",
                "-pix_fmt",
                "yuv420p",
            ]
            process_and_save_image(input_path, path_raw, args_raw)

            vf_inline = "scale='min(960,iw)':-2"
            path_inline = os.path.join(directory, "processed.avif")

            args_inline = [
                "-vf",
                vf_inline,
                "-threads",
                "2",
                "-c:v",
                "libaom-av1",
                "-still-picture",
                "1",
                "-crf",
                "26",
                "-cpu-used",
                "6",
                "-pix_fmt",
                "yuv420p",
            ]
            process_and_save_image(input_path, path_inline, args_inline)

    return f"Successfully processed {section} for {relative_path}"
