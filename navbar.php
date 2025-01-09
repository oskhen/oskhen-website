
<nav class="navbar">
    <ul>
        <li><a href="/">Home</a></li>
        <li class="dropdown">
            <a href="/projects">Projects</a>
            <ul class="dropdown-menu">
                <?php

                    $cwd = dirname(__FILE__);
                    $db = new SQLite3("$cwd/projects.db");
                    $results = $db->query("SELECT * FROM projects");
                    while ($row = $results->fetchArray()) {

                        $title = $row['display_name'];
                        $url = $row['url_root'];
                        echo "<li><a href='$url'>$title</a></li>";
                    }
                ?>
            </ul>
        </li>
        <li><a href="https://github.com/oskhen">Github</a></li>
    </ul>
</nav>
