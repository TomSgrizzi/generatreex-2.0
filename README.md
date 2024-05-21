# GeneraTreeX 2.0 User Guide

Welcome to GeneraTreeX 2.0, a tool designed to swiftly generate syntactic trees from in-line notation. This user-friendly application simplifies the process of creating complex syntactic tree diagrams for linguistic analysis and studies. 

### Previous versions
You can check GeneraTreeX 1.0 [here](https://generatreex-f84b761a7ce0.herokuapp.com/), refer to its [GitHub repository](https://github.com/TomSgrizzi/generatreex) for more information.

## New features and improvements
+ Possibility to optionally specify the in and out directions of movement lines.
+ New download options: LaTeX code and transparent png file alongside the PDF file.
+ Availability of mobile interface.
+ Layout simplification (from 4 pages down to 2).

## What is GeneraTreeX?

GeneraTreeX is a web application that allows users to input a specific in-line notation syntax to produce syntactic tree diagrams. It's ideal for linguists, educators, and students who need to visualize the structure of sentences according to syntactic theory.

## Getting Started

To use GeneraTreeX, navigate to the application's webpage. You will be presented with an intuitive interface that guides you through the process of creating your syntactic tree.

## Input Format

The input for GeneraTreeX must follow a specific in-line notation. The notation should begin with an opening square bracket `[` and end with a closing square bracket `]`. Within these brackets, you will define the structure of your tree.

### Example Input

Here is a sample input that demonstrates the expected format:

```
[S [NP [D The] [N cat]] [VP [V sat] [PP [P on] [NP [D the] [N mat]]]]]
```
You can click on __Autofill__ to automatically fill in all the fields with an example. Click __Submit__ to see the output.

## Steps for Generating a Syntactic Tree

1. **Structure Input**: Enter your syntactic structure in the provided text area using the in-line notation format.

2. **Movement lines**: You will be asked to select how many movement lines you want to represent (default is 0).

3. **Node Labels**: If you choose to add movement lines, you will have to submit pairs of node labels that you wish to connect with movement lines. The probes will go in the _from_ input field, and the respective goals will go in the _to_ input field, separated by a comma: `DP1, DP2`. For instance: if you want a line connecting `DP1 -> DP2`, and a line connecting `V -> T`, you will have to enter `DP1,V` into _from_ and `DP2,T` into _to_.

4. **Movement Directions (optional)**: In addition to the node labels you may specify what directions will take the lines both when exiting their origin node and when they enter their landing node. If you do not provide an equal number of directions for both output and input directions GeneraTreeX will automatically compute the standard ones. These are the following parameters accepted:
+ `north` ⬆️
+ `east` ➡️
+ `south` ⬇️
+ `west` ⬅️

And they must be entered following the same pattern of the node labels. For instance: `DP2,T` will be paired with `north,south` if you want the line exiting DP from the upper side of the node and arriving to T from below.

5. **Download**: Once you click __submit__ the tree diagram is displayed, and you will access the PDF file, the LaTeX code, and the PNG transparent file.

## Error Handling

While using GeneraTreeX, you may encounter the following errors:

- **Improper Starting Bracket**: Your input must start with an opening square bracket `[`. If it doesn't, you will be prompted to correct your input.

- **Bracket Mismatch**: The application checks for an equal number of opening and closing brackets. If they don't match, you will be alerted to fix the bracketing in your input.

- **Movement Line Errors**: If you provide node pairs that are improperly formatted or incomplete, the application will notify you and ask for the correct input.

- **Server-Side Errors**: Errors during the PDF generation process, such as a timeout or a LaTeX compilation issue, will result in error messages explaining the problem.

## Best Practices

- Ensure that node labels used for movement lines are unique within your entire tree.

- Review your input for typos or syntax errors before confirming the structure.

- Use a modern browser for the best experience.

GeneraTreeX is designed to be a straightforward and efficient tool for visualizing syntactic structures. We hope this guide helps you use the application effectively. Enjoy creating your syntactic trees!
