function autofill() {
    // Select all the input fields you want to fill
    document.querySelector('input[name="structure"]').value = "[CP [DP [What]] [C' [C [does]] [TP [DP1 [this GeneraTreeX]] [T' [T] [VP [DP2] [V' [V [do]][DP3]]]]]]]";
    document.querySelector('select[name="movement_lines"]').value = '3';
    document.querySelector('input[name="from_nodes"]').value = 'DP3,T,DP2';
    document.querySelector('input[name="to_nodes"]').value = 'DP,does,DP1';
    document.querySelector('input[name="direction_out"]').value = 'north,west,south';
    document.querySelector('input[name="direction_in"]').value = 'east,south,west';
  
    console.log("");
    console.log("Autofill function executed.");
    console.log("Structure: " + document.querySelector('input[name="structure"]').value);
    console.log("Movement Lines: " + document.querySelector('select[name="movement_lines"]').value);
    console.log("From Nodes: " + document.querySelector('input[name="from_nodes"]').value);
    console.log("To Nodes: " + document.querySelector('input[name="to_nodes"]').value);
    console.log("Direction Out: " + document.querySelector('input[name="direction_out"]').value);
    console.log("Direction In: " + document.querySelector('input[name="direction_in"]').value);
    // Add more lines for each input field you want to autofill
  }
  