## About How to use Phph Browse Server to Check the Details
If you need to extract Java project, please refer to read me.md of [phph]( https://github.com/salab/phph/).<br>
To extract python projects:<br>
### Build
```
$ git clone https://github.com/salab/phph.git
$ cd phph
$ git branch-a|cat
$ git checkout merge-durun-phph
$ git submodule init
$ git submodule update
$ ./gradlew shadowJar
$ java -jar build/libs/phph-all.jar <cmd> [options...]
```
<br>

### Usage
```
$ java -jar phph-all.jar init                                    # initalize database
$ java -jar phph-all.jar extract --splitter=python3 --repository=/path/to/repo/.git # extract patterns
$ java -jar phph-all.jar find                                    # find pattern application opportinuties
$ java -jar phph-all.jar measure                                 # compute metric values
```
<br>

### Browse Server
```
$ java -jar phph-all.jar browse                                            
```
<br><br>

