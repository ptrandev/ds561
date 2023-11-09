import argparse
import logging
import re
import time

import apache_beam.io.fileio
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class IncomingLinkCount(beam.DoFn):
    def process(self, element):
        regex = re.compile(r'<a HREF="(\d+).html">')
        links = re.findall(regex, element)
        for link in links:
            yield (int(link), 1)


def run(argv=None, save_main_session=True):
    """Main entry point; defines and runs the wordcount pipeline."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        dest="input",
        default="gs://ds561-ptrandev-hw02/html/*.html",
        help="Input files to process.",
    )
    known_args, pipeline_args = parser.parse_known_args(argv)

    # We use the save_main_session option because one or more DoFn's in this
    # workflow rely on global context (e.g., a module imported at module level).
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = save_main_session

    start = time.time()

    # The pipeline will be run on exiting the with block.
    with beam.Pipeline(options=pipeline_options) as p:
        input_files = known_args.input

        # Find the incoming links for each file
        incoming_links = (
            p
            | "Read HTML Files as Stream" >> beam.io.ReadFromText(input_files)
            | "Count Incoming Links" >> beam.ParDo(IncomingLinkCount())
            | "Sum Incoming Links" >> beam.CombinePerKey(sum)
        )

        # Find the outgoing links for each file
        outgoing_links = (
            p
            | "List Files" >> beam.io.fileio.MatchFiles(input_files)
            | "Read Matches" >> beam.io.fileio.ReadMatches()
            | "Read Files" >> beam.Map(lambda x: (x.metadata.path, x.read_utf8()))
            # for each file, sum up the number of <a HREF="*.html"> links that it contains
            | "Count Outgoing Links"
            >> beam.Map(
                lambda x: (x[0], len(re.findall(r'<a HREF="(\d+).html">', x[1])))
            )
            # for each key, remove the file path and keep the file number
            | "Remove File Path"
            >> beam.Map(lambda x: (int(x[0].split("/")[-1].split(".")[0]), x[1]))
        )

        # Find the top 5 files with the most incoming links
        top_incoming_links = (
            incoming_links
            | "Top 5 Incoming Links" >> beam.transforms.combiners.Top.Largest(
                5, key=lambda x: x[1]
            )
        )

        # Find the top 5 files with the most outgoing links
        top_outgoing_links = (
            outgoing_links
            | "Top 5 Outgoing Links" >> beam.transforms.combiners.Top.Largest(
                5, key=lambda x: x[1]
            )
        )

        # log the top 5 incoming links with the title "Top 5 Incoming Links"
        top_incoming_links | "Log Top 5 Incoming Links" >> beam.Map(
            lambda x: logging.info(f"Top 5 Incoming Links: {x}")
        )

        # log the top 5 outgoing links with the title "Top 5 Outgoing Links"
        top_outgoing_links | "Log Top 5 Outgoing Links" >> beam.Map(
            lambda x: logging.info(f"Top 5 Outgoing Links: {x}")
        )


    print(f"Total time: {time.time() - start} seconds")

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    run()