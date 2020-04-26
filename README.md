# wp-to-hugo-scripts

Scripts that I used to convert wordpress contents into a hugo-compatible markdown formats.

## Prerequisites

```sh
# Execute the following command in the server that hosts your WordPress website
$ cd /path/to/your/wp-content/plugins
$ git clone git@github.com:SchumacherFM/wordpress-to-hugo-exporter.git
$ cd wordpress-to-hugo-exporter
$ php hugo-export-cli.php > export.zip
```

## Usage

Suppose that `${EXPORT_ROOT}` is the path where `export.zip` is extracted.

### 1. Update directory structure to page bundled style

Convert contents into the page bundled style.

```sh
$ python scripts/update_directory_structure.py ${EXPORT_ROOT}/posts
```

#### Example

- Before
  ```
  posts
  ├── 2018-08-29-hoge.md
  ├── 2019-10-20-fuga.md
  ```
- After
  ```
  posts
  ├── 2018-08-29-hoge
  │   └── index.md
  ├── 2019-10-20-fuga
  │   └── index.md
  ```

### 2. Convert `<pre>` into a code block

Convert `<pre>` into a codeblock.
The script supports:
- Handle `lang:`, `mark`, and `title` attributes
- Decode `&lt;` and `&gt;` into `<` and `>`, respectively.

```sh
$ python scripts/convert.py ${EXPORT_ROOT}/posts code
```

#### Example

- Before
  ```
  <pre class="striped:false lang:xhtml mark:5 decode:true " title="NuGet.Config" >&lt;?xml version="1.0" encoding="utf-8"?&gt;
  &lt;configuration&gt;
    &lt;packageSources&gt;
      &lt;add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" /&gt;
      &lt;add key="local-nugets" value="/path/to/directory/of/nuget/repository" /&gt;
    &lt;/packageSources&gt;
  &lt;/configuration&gt;</pre>
  ```
- After
  ```md
  ```xhtml {hl_lines=["5"],linenos=table}
  <?xml version="1.0" encoding="utf-8"?>
  <configuration>
    <packageSources>
      <add key="nuget.org" value="https://api.nuget.org/v3/index.json" protocolVersion="3" />
      <add key="local-nugets" value="/path/to/directory/of/nuget/repository" />
    </packageSources>
  </configuration>```
  ```


### 3. Convert image contents

Convert image contents into a hugo-compatible format (shortcode).
Also move image files to page bundle resources.
The script supports:
- Handle an element that has `wp-caption-text` class as an image caption
- Use the original image for the entry if a resized image is set to `src` of `<img>`.

```sh
$ python scripts/convert.py ${EXPORT_ROOT}/posts img [YOUR PREVIOUS WEBSITE DOMAIN]/wp-content/uploads/ ${EXPORT_ROOT}/wp-content/uploads/
```

#### Example

- Before
  ```
  posts
  ├── 2018-08-29-hoge
  │   └── index.md
  ├── 2019-10-20-fuga
  │   └── index.md
  ```
  - `2019-10-20-fuga/index.md`
    ```md
    <div class="wp-caption alignnone">
      <a href="http://example.com/wp-content/uploads/2019/10/image.png"><img src="http://example.com/wp-content/uploads/2019/10/image-300x400.png" alt="Image Caption" /></a>
      <p class="wp-caption-text">
        Image Caption
      </p>
    </div>
    ```

- After
  ```
  posts
  ├── 2018-08-29-hoge
  │   ├── index.md
  │   ├── image.png
  │   └── image2.png
  ├── 2019-10-20-fuga
  │   ├── index.md
  │   └── image.png
  ```
  - `2019-10-20-fuga/index.md`
    ```md
    {{<figure src="image.png" title="Image Caption" alt="Image Caption" >}}
    ```
