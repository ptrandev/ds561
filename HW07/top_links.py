import apache_beam as beam
import re
import argparse
import time


class IncomingLinkCount(beam.DoFn):
    def process(self, element):
        regex = re.compile(r'<a HREF="(\d+).html">')
        links = re.findall(regex, element)
        for link in links:
            yield (int(link), 1)

def run(input_files):
    start = time.time()

    with beam.Pipeline() as p:
        incoming_links = (
            p
            | "Read HTML Files" >> beam.io.ReadFromText(input_files)
            | "Count Incoming Links" >> beam.ParDo(IncomingLinkCount())
            | "Sum and Combine Incoming Links" >> beam.CombinePerKey(sum)
        )

        # Find and print the top 5 files with the most incoming links
        incoming_links | "Top 5 Incoming Links" >> beam.transforms.combiners.Top.Largest(
            5, key=lambda x: x[1]
        ) | "Print Top 5 Incoming Links" >> beam.Map(
            print
        )

    print(f"Total time: {time.time() - start} seconds")


def run_cloud(bucket, directory):
    print("Running on the cloud...")
    run(f"gs://{bucket}/{directory}*.html")


def run_local(directory):
    print("Running locally...")
    run(f"{directory}0.html")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--bucket",
        type=str,
        default="ds561-ptrandev-hw02",
        help="The name of the Google Cloud Storage bucket (default: ds561-ptrandev-hw02)",
    )

    parser.add_argument(
        "--directory",
        type=str,
        default="html/",
        help="The directory path to the HTML files in the bucket (default: html/))",
    )

    parser.add_argument(
        "--local",
        type=bool,
        default=False,
        help="Run the pipeline locally (default: False)",
    )

    bucket = parser.parse_args().bucket
    directory = parser.parse_args().directory
    local = parser.parse_args().local

    if local:
        run_local(directory)
    else:
        run_cloud(bucket, directory)
