# DS561 HW07

## Program Setup

To run the locally program, setup a virtual environment and install the requirements:

```
$ python3 -m venv venv
$ source venv/bin/activate
$ pip3 install -r requirements.txt
```

## Program Options

The `top_links.py` program has 2 options:

- `--input` - The directory pattern for input files to process. The default is `gs://ds561-ptrandev-hw02/html/*.html`

## Running the program

If you just need to run the program with default options, you can run it with the following command:

```markdown
$ python3 -m top_links
```

This will run the program with the default options. If you want to run the program with different options, here is an example:

```
$ python3 top_links.py --input gs://bucket-name/path/to/*.html
```

Now to run it on the cloud you'll need additional options. Here is an example:
```
$ python3 -m top_links --region us-east4 --runner DataflowRunner --project ds561-trial-project --temp_location=gs://ds561-ptrandev-hw07/tmp --staging_location=gs://ds561-ptrandev-hw07/staging
```