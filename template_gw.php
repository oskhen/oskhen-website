<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="/styles.css">
</head>
<body>

    <?php
    #error_reporting(E_ALL);
    #ini_set('display_errors', 'On');

function getAdjacentID($db, $currentID) {

        $entries = [];

        $results = $db->query("SELECT * FROM entries ORDER BY date asc");

        while ($row = $results->fetchArray()) {

           array_push($entries, $row["id"]); 

        }

        $currentIndex = array_search($currentID, $entries);
        
        $prev = $next = $currentID;

        if ($currentIndex > 0) {$prev = $entries[$currentIndex - 1];}
        if ($currentIndex < count($entries) - 1) {$next = $entries[$currentIndex + 1];}

        $adjacentIDs = [$prev, $next];
        return $adjacentIDs;

}

function getRandomID($db) {

    $entries = [];

    $results = $db->query("SELECT * FROM entries");
    while ($row = $results->fetchArray()) {

       array_push($entries, $row["id"]); 

    }

    $randomID = $entries[array_rand($entries)];
    return $randomID;
}


    
    $requestURI = htmlspecialchars($_SERVER['REQUEST_URI']);
    $rootURI = implode('/', array_slice(explode('/', $requestURI), 0, -1)) . "/";

    $projectDB = new SQLite3('projects.db');

    $statement = $projectDB->prepare("SELECT * FROM projects WHERE url_root=:URI");
    $statement->bindValue(":URI", $rootURI, SQLITE3_TEXT);
    $project = $statement->execute()->fetchArray();
    
    if (!$project) {
        header("HTTP/1.0 404 Not Found");
        echo "<h1> File not found!</h1>";
        echo "<a href='https://oskhen.se'>Go Home!</a>";
        return;
    }

    //echo '<pre>'; print_r($project); echo '</pre>';

    $contentRoot = $project["content_root"];
   
    $db = new SQLite3(".$contentRoot/entries.db");

    $requestedID = urldecode($_GET['id']);

    $adjacentID = getAdjacentID($db, $requestedID);
    $randomID = getRandomID($db);

?>


    <div class="navbar">
        <ul>
            <?php echo "<li><a href='{$rootURI}'>Home</a></li> ";?>
            <?php echo "<li><a href='template.php?id={$randomID}'>Random</a></li> ";?>
            <?php echo "<li><a href='template.php?id={$adjacentID[0]}'>Previous</a></li> ";?>
            <?php echo "<li><a href='template.php?id={$adjacentID[1]}'>Next</a></li>";?>
        </ul>
    </div>
    
    <div class="content about-section">

<?php

    if (!$requestedID == "") {

        $statement = $db->prepare("SELECT * FROM entries WHERE id=:id");
        $statement->bindValue(":id", $requestedID, SQLITE3_INTEGER);
        $result = $statement->execute();
        
        while ($row = $result->fetchArray()) {
        
            $contentFile = ".$contentRoot/entries/{$row['section']}/{$row['title']}.html";

            $timestamp = $row["date"]; 
            echo "<h1>" . $row["title"] . "</h1>";
            echo "<p><small>" . date("Ymd - H:i", $timestamp) . "</small></p>";

            $statement = $db->prepare("UPDATE entries SET viewcount = viewcount + 1 WHERE id=:id");
            $statement->bindValue(":id", $requestedID, SQLITE3_INTEGER);
            $statement->execute();

            include $contentFile;

        }
    } else {
     header("HTTP/1.0 404 Not Found");
     echo "<h1> File not found!</h1>";
     echo "<a href='https://oskhen.se'>Go Home!</a>";
     return;
    }
    ?>

    </div>
    
    <script src="script.js"></script>
</body>
</html>
