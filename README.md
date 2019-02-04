# Close-By-One with Implications (`CbOI`)

## Installation

1. Install Python 2.7.12
2. Run `pip install -r requirements`

## Usage
Run `python main.py -h` to get help

## Contexts and Implications
Example of contexts and implications files are provided in [/data](/data). For instance:
* [/data/Example/input.data](/data/Example/input.data) represents a formal context where each line represents the set of items (i.e. the intent) of an object.
* [/data/Example/input.implications](/data/Example/input.implications) represent the provided item-implication basis. Each line presents a pair of items `a	b` representing the item-implication `a → b`.

## Scaling Complex Attributes
We provide a small tool to generate given a dataset with complex attributes (nominal, ordinal or numerical), the associated context and set of implications. An example of such a dataset is given in [/data/Example/input.csv](/data/Example/input.csv).
### Command
Runing `python main.py scale data/Example/input.csv` will generate a context `python main.py scale data/Example/input.data` and a set of implications `python main.py scale data/Example/input.implications` according to the columns annotations in the input file (See Details Below).
  
### Details
Each column is annotated by the type of scale to use (**nominal**, **ordinal** or **interordinal**):
* **nominal:** any value is accepted, the result of nominal scaling is transforming each value `v` to an item `attr=v`. No implication is generated post nominal scaling.
* **ordinal:** values need to be in the form `x.y.z` provided that `x ≤ x.y ≤ x.y.z`, the result of ordinal scaling of such an attribute `attr` is transforming each value `x.y.z` to the set of item `attr-is-x`, `attr-is-x.y` and `attr-is-x.y.z`. The associated item-implications are `attr-is-x.y.z → attr-is-x.y` and `attr-is-x.y → attr-is-x`
* **interordinal:** values need to be numerical. Given an attribute `attr` whose values are `{1, 2, 3}` and an object which value is `attr=2`. The associated set of items is: `{attr≤2, attr≤3, attr≥1, attr≥2}`. The set of implications is given by `{attr≤1 → attr≤2, attr≤2 → attr≤3, attr≥3 → attr≥2, attr≥2 → attr≥1}`.  
   

## Examples of running `CbO` and `CbOI`
1. Run `CbO` on a context (`-v` for printing patterns):
`python main.py cbo -d data/Example/input.data -v` 

2. Run `CbOI` on a context with its implications (`-v` for printing patterns)
`python main.py cboi -d data/Example/input.data -i data/Example/input.implications -v` 

3. Run `CbOI` on a context and compute the total set of item-implications from the input context
`python main.py cboi -d data/Example/input.data -c`

* Other commands are provided like `subdataset`, `test` and `test_densities`. Please see the provided help to use these commands.


