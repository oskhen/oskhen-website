<!DOCTYPE html>
<html>
<head>
    <title>Directory Listing</title>
    <link rel="stylesheet" href="/styles.css">
    <script src="script.js"></script>
</head>
<body>
<?php
#error_reporting(E_ALL);
#ini_set('display_errors', 'On'); 

include("navbar.php");

echo "<div class='container'>";

$RECENTLY_UPLOADED_MAX_ROWS = 20;
$RECENTLY_UPLOADED_TIME_LIMIT = 864000; # seconds until fade, currently 10 days

$requestURI = htmlspecialchars($_SERVER['REQUEST_URI']);
#echo "$requestURI<br>";

$projectDB = new SQLite3('projects.db');
$content = [
"order" => 0,
"entries" => [],
"childs" => [],
];


function getHREFbyID ($contentRoot, $ID, $title) {

    #$encodedID = ".$contentRoot/template.php?id=$ID";
    $encodedID = "./template.php?id=$ID";
    return "<a href='$encodedID'>$title</a>";
}

function getFavorites($favorites) {

    $favoriteArray = [];

    if (file_exists($favorites)) {
        $lines = file($favorites, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
        foreach ($lines as $line) {
            array_push($favoriteArray, $line);
        }
    }
    return $favoriteArray;
}

$statement = $projectDB->prepare("SELECT * FROM projects WHERE url_root=:URI");
$statement->bindValue(":URI", $requestURI, SQLITE3_TEXT);
$project = $statement->execute()->fetchArray();
//echo '<pre>'; print_r($project); echo '</pre>';

if (!$project) {
    header("HTTP/1.0 404 Not Found");
    echo "<h1> File not found!</h1>";
    echo "<a href='https://oskhen.se'>Go Home!</a>";
    return;
}

$contentRoot = $project["content_root"];
$recentlyUploadedFlag = $project["recently_uploaded"];
$db = new SQLite3(".$contentRoot/entries.db");

include("./$contentRoot/about.html");

$recentlyUploaded = [];
$favorites = getFavorites(".{$contentRoot}/favorites.txt");

$results = $db->query("SELECT * FROM (SELECT * FROM entries ORDER BY date desc LIMIT $RECENTLY_UPLOADED_MAX_ROWS) ORDER BY date asc");
while ($row = $results->fetchArray()) {

    if (time() - $row['date'] < $RECENTLY_UPLOADED_TIME_LIMIT) {
        array_push($recentlyUploaded, [getHREFbyID($contentRoot, $row["id"], $row["title"]), $row["section"]]);
    }
}

$results = $db->query('SELECT * FROM entries ORDER BY date asc');
while ($row = $results->fetchArray()) {
    $sections = explode("/", $row["section"]);
    $dir = &$content;

    foreach ($sections as $section) {

        if (!array_key_exists($section, $dir["childs"]))
        {
            $dir["childs"][$section] = [
                "order" => 0,
                "entries" => [],
                "childs" => []
            ];
        } 

        $dir = &$dir["childs"][$section];
    }

    array_push($dir["entries"], [$row["id"], $row["title"]]);
}

// Read the "priority.txt" file.
$priorityFile = ".{$contentRoot}/priority.txt";
$currentOrder = 0;

if (file_exists($priorityFile)) {
    $lines = file($priorityFile, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {

        $sections = explode("/", $line);
        $dir = &$content;

        foreach ($sections as $section) {
            if (array_key_exists($section, $dir["childs"]))
            {
                $dir["childs"][$section]["order"] = $currentOrder;
                $dir = &$dir["childs"][$section];
            } else {
                break;
            }
        }
        $currentOrder++;
    }
}


function displayEntries($contentRoot, $content, $name, $currentPath, $depth) {

    global $favorites;

    $dirs = array_keys($content["childs"]);
    //echo '<pre>'; print_r($dirs); echo '</pre>';

    usort($dirs, function ($lhs, $rhs) use ($content) {
        $int_lhs = $content["childs"][$lhs]["order"];
        $int_rhs = $content["childs"][$rhs]["order"];
        if ($int_lhs == $int_rhs) return 0;
        return ($int_lhs < $int_rhs) ? -1:1;
           
    });

        //echo "$name ; $depth ; $currentPath ; $contentRoot";
        if ($name != "")
            echo "<h$depth>$name</h$depth>";

        foreach ($content["entries"] as $entry) {
            $href = getHREFbyID($contentRoot, ...$entry);
            if (in_array($entry[0], $favorites)) {
                echo "{$href} - ★ <br>";
            } else {
                echo "{$href}<br>";
            } 
        }

    foreach ($dirs as $child) {
        displayEntries($contentRoot, $content["childs"][$child], $child, $currentPath . "/" . $child, $depth+1);
    }

}


if ($recentlyUploadedFlag) {

    if ($recentlyUploaded) {

        echo "<h1>Recently Uploaded</h1>";
        foreach ($recentlyUploaded as $entry) {echo "$entry[0]<br>";}
        //foreach ($recentlyUploaded as $entry) {echo "$entry[0] - $entry[1]<br>";}
    }
    else {
        //echo "<p> There doesn't seem to be anything here.. </p><br>";
    }
}

displayEntries($contentRoot, $content, "", "", 0);

?>

    </div>
</body>
</html>
