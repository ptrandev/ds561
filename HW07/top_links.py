import apache_beam as beam
import re
import argparse

class LinkCount(beam.DoFn):
    def process(self, element):
        regex = re.compile(r'<a HREF="(\d+).html">')
        links = re.findall(regex, element)
        for link in links:
            yield (link, 1)

def run(bucket, directory):
    with beam.Pipeline() as p:
        # Read HTML files from your Cloud Storage bucket
        input_files = f"gs://{bucket}/{directory}*.html"

        incoming_links = (
            p
            | "Read HTML Files" >> beam.io.ReadFromText(input_files)
            | "Count Incoming Links" >> beam.ParDo(LinkCount())
            | "Group by URL" >> beam.GroupByKey()
            | "Sum Incoming Links" >> beam.CombineValues(sum)
        )

        outgoing_links = (
            incoming_links
            | "Flatten Incoming Links" >> beam.FlatMap(lambda x: [(url, 0) for url in x[0]])
            | "Count Outgoing Links" >> beam.CombinePerKey(sum)
        )

        # Find and print the top 5 files with the most incoming links
        incoming_links | "Top 5 Incoming Links" >> beam.transforms.combiners.Top.Largest(5, key=lambda x: x[1]) | "Print Top 5 Incoming Links" >> beam.Map(print)

        # Find and print the top 5 files with the most outgoing links
        outgoing_links | "Top 5 Outgoing Links" >> beam.transforms.combiners.Top.Largest(5, key=lambda x: x[1]) | "Print Top 5 Outgoing Links" >> beam.Map(print)

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

    run(**vars(parser.parse_args()))