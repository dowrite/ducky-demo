/**
 * Created by Kristiana Rendon on 7/3/2017.
 */
var row_num = 0;
var refresh_rate = 1000;
var refresher = setInterval("refreshTable();", refresh_rate);
var database_size = 0;


function refreshTable() {
    $.ajax({
        type: 'POST',
        contentType: "application/json",
        url: '/get_updates',
        dataType: 'json',
        success: function(data) { //gets data from python function in the form of a list/array
           console.log("refreshing the table");
            for (var counter = 0; counter < parseInt(data[0][6]); counter++) {
                var cell = document.getElementById("password_table").rows[counter + 1].cells;
                cell[0].innerHTML = counter; //row number
                cell[1].innerHTML = data[counter][0]; //password
                cell[2].innerHTML = data[counter][1]; //hash
                cell[3].innerHTML = data[counter][2]; //tries
                cell[4].innerHTML = data[counter][3]; //elapsed_time
                cell[5].innerHTML = data[counter][4]; //status
                cell[6].innerHTML = data[counter][5]; //source
             }
        },
        error: submitPasswordFailureRefresh
    });
}

//function refreshTable() {
//    for (var counter = 0; counter < row_num; counter++) {
////        //we want to ignore the table header row
//        var cell = document.getElementById("password_table").rows[counter + 1].cells;
//        var hashed_password = cell[2].innerHTML;
////        //retrieve data from python's call to
//        $.ajax({
//            type: 'POST',
//            contentType: "application/json",
//            url: '/get_updates',
//            dataType: 'json',
//            data: JSON.stringify({"hash" : hashed_password.toString()}),
//            success: function(data) { //gets data from python function in the form of a list/array
//                cell[0].innerHTML = counter;
//                cell[1].innerHTML = data.password;
//                cell[3].innerHTML = data.tries;
//                cell[4].innerHTML = data.elapsed_time;
//                cell[5].innerHTML = data.status;
//                cell[6].innerHTML = data.source;
//            },
//            error: submitPasswordFailureRefresh
//        });
//    }
//}

function submitPassword() {
    var initial_password = document.getElementById('password_input').value; //gets the initially entered password
    var confirmed_password = document.getElementById('password_input_confirm').value; //gets the confirmed entered password

    if(checkPassword(initial_password, confirmed_password))
    {
        var hashed_password = CryptoJS.MD5(confirmed_password);
        update_table(hashed_password);
        document.getElementById("hashContent").innerHTML = "<h3>" + hashed_password + "</h3>"; //updates last hash added
        $.ajax({
            type: 'POST',
            url: '/crack_password',
            contentType: "application/json",
            data: JSON.stringify({"hash" : hashed_password.toString()}),
            success: submitPasswordSuccess,
            error: submitPasswordFailure
        });
    }
    document.getElementById('password_input').value = ""; //resets input box
    document.getElementById('password_input_confirm').value = ""; //resets input box
}

function checkPassword(initial_password, confirmed_password) {
    if(initial_password == confirmed_password && confirmed_password.length == 12)
    {
        return true;
    }
    else if(initial_password == confirmed_password && confirmed_password.length < 12)
    {
        alert("Password length is less than 12. Please try again.");
    }
    else if(initial_password == confirmed_password && confirmed_password.length > 12)
    {
        alert("Password length is greater than 12. Please try again.");
    }
    else if (initial_password != confirmed_password)
    {
        alert("Passwords do not match. Please try again.");
    }
    return false;
}

function submitPasswordFailure() {
    console.log("password failed");
}

function submitPasswordFailureRefresh() {
    console.log("refresh failed");
}

function submitPasswordSuccess(data) {
    console.log("password success");
}

function update_table(hashed_password) {
    $.ajax({
        type: 'POST',
        url: '/get_table_size',
        success: update_table_success,
        failure: update_table_failure
    })
}

function update_table_success(data) {
    // if there are fewer than 10 hashes in the database, show additional rows
    console.log(parseInt(data));
    if (parseInt(data) < 10)
    {
        var table = document.getElementById("password_table"); //gets table ID
        var row = table.insertRow(-1); //creates row <tr>
        var scope = row.insertCell(0); //creates cell <td>
        var insert_password = row.insertCell(1); //creates cell <td>
        var insert_hashed_value = row.insertCell(2); //creates cell <td>
        var insert_tries = row.insertCell(3); //creates cell <td>
        var insert_elapsed_time = row.insertCell(4); //creates cell <td>
        var insert_status = row.insertCell(5); //creates cell <td>
        var insert_source = row.insertCell(6); //creates source <td>

        scope.innerHTML = row_num.toString();
        row_num++; //increment scope/label number
        insert_password.innerHTML = "************"; //filler password until the password is cracked
        insert_hashed_value.innerHTML = hashed_password; //writes MD5 hash for password into proper cell
        insert_tries.innerHTML = "...";
        insert_elapsed_time.innerHTML = "...";
        insert_status.innerHTML = "Pending"
        insert_source.innerHTML = "WEB";
    }
}

function update_table_failure() {
    console.log("update_table_failure.")
}
