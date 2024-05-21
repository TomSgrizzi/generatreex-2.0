# GeneraTreeX User Guide

Welcome to GeneraTreeX, a robust tool designed to swiftly generate syntactic trees from in-line notation. This user-friendly application simplifies the process of creating complex syntactic tree diagrams for linguistic analysis and studies.

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

## Steps for Generating a Syntactic Tree

1. **Structure Input**: Enter your syntactic structure in the provided text area using the in-line notation format.

2. **Validation**: The application will check if your structure begins with an opening square bracket `[`. If not, you will receive an error prompting you to correct your input.

3. **Bracket Balance**: The app will verify that the number of opening brackets `[` matches the number of closing brackets `]`. Mismatched brackets will result in an error.

4. **Confirmation**: Once your input is validated, you will be asked to confirm if you want to represent movement lines in your syntactic tree.

5. **Movement Lines (Optional)**: If you choose to add movement lines, you will be instructed to submit pairs of node labels that you wish to connect with movement lines. Each pair should be separated by a comma. For example: `DP1, DP2`.

6. **Proceed**: After submitting the node pairs, click on the "Proceed" button to generate your diagram.

7. **Download**: Once the tree diagram is generated, you will be redirected to a page where you can download the PDF file of your syntactic tree.

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