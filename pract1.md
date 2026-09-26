# **Практическое занятие №1. Введение, основы работы в командной строке**

 **Цель:** научиться выполнять простые действия с файлами и каталогами в Linux из командной строки. Сравнить работу в командной строке Windows и Linux.
 
 **Система:** Tahoe 26, zsh. Все скрипты проверены в ShellCheck, предупреждений нет.

 ## **Задача 1**

Вывести отсортированный в алфавитном порядке список имен пользователей в файле passwd.

```
mihailborzenkov@MacBook-Air-Mihail-5 ~ % grep -v "^#" /etc/passwd | cut -d: -f1 | sort    
_accessoryupdater
_amavisd
_analyticsd
_aonsensed
_appinstalld
_appleevents
_applepay
_appowner
_appserver
_appstore
_ard
_assetcache
_astris
_atsserver
_audiomxd
_avbdeviced
_avphidbridge
_backgroundassets
_biome
_calendar
_captiveagent
_ces
_clamav
_cmiodalassistants
_coreaudiod
_coremediaiod
_coreml
_corespeechd
_ctkd
_cvmsroot
_cvs
_cyrus
_darwindaemon
_datadetectors
_demod
_devdocs
_devicemgr
_diagnosticservicesd
_diskimagesiod
_displaypolicyd
_distnote
_dovecot
_dovenull
_dpaudio
_driverkit
_eligibilityd
_eppc
_findmydevice
_fpsd
_ftp
_gamecontrollerd
_geod
_hidd
_iconservices
_installassistant
_installcoordinationd
_installer
_jabber
_kadmin_admin
_kadmin_changepw
_knowledgegraphd
_krb_anonymous
_krb_changepw
_krb_kadmin
_krb_kerberos
_krb_krbtgt
_krbfast
_krbtgt
_launchservicesd
_lda
_locationd
_logd
_lp
_mailman
_mbsetupuser
_mcxalr
_mdnsresponder
_mds_stores
_mmaintenanced
_mobileasset
_mobilegestalthelper
_modelmanagerd
_mysql
_naturallanguaged
_nearbyd
_netbios
_netstatistics
_networkd
_neuralengine
_notification_proxy
_nsurlsessiond
_oahd
_ondemand
_postfix
_postgres
_qtss
_reportmemoryexception
_reportsystemmemory
_rmd
_sandbox
_screensaver
_scsd
_securityagent
_sntpd
_softwareupdate
_spinandd
_spotlight
_sshd
_svn
_swtransparencyd
_systemstatusd
_taskgated
_teamsserver
_terminusd
_timed
_timezone
_tokend
_trustd
_trustevaluationagent
_unknown
_update_sharing
_usbmuxd
_uucp
_warmd
_webauthserver
_windowserver
_www
_wwwproxy
_xserverdocs
daemon
nobody
root
```

## **Задача 2**

Вывести данные /etc/protocols в отформатированном и отсортированном порядке для 5 наибольших портов.

```
mihailborzenkov@MacBook-Air-Mihail-5 ~ % grep -v "^#" /etc/protocols | awk 'NF {print $2, $1}' | sort -nr | head -5 
258 divert
240 pfsync
142 rohc
141 wesp
140 shim6
```

## **Задача 3**

Написать программу banner средствами bash для вывода текстов в рамке.

Код `banner`:

```
#!/bin/bash

text="$1"
len=${#text}
line=$(printf -- '-%.0s' $(seq 1 $((len + 2))))

echo "+${line}+"
echo "| ${text} |"
echo "+${line}+"
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x banner 
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck banner
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./banner 'Hello from RTU MIREA!'
+-----------------------+
| Hello from RTU MIREA! |
+-----------------------+
```

## **Задача 4**

Написать программу для вывода всех идентификаторов в файле без повторений.

Текстовый файл `hello.c`:

```
#include <stdio.h>

int main(void) {
    printf("hello world\n");
    return 0;
}
```

Код `idents`:

```
#!/bin/bash
if [ $# -ne 1 ]; then
    echo "Usage: $0 file" >&2
    exit 1
fi

grep -oE '[A-Za-z_][A-Za-z0-9_]*' "$1" | sort -u | tr '\n' ' '
echo
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x idents
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck idents
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./idents hello.c
h hello include int main n printf return stdio void world 
```

## **Задание 5**

Написать программу для регистрации пользовательской команды, устанавливает правильные права доступа и копирует файл в /usr/local/bin.

Код `reg`:

```
#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 file" >&2
    exit 1
fi

if [ ! -f "$1" ]; then
    echo "Error: $1 not found" >&2
    exit 1
fi

sudo install -m 755 "$1" /usr/local/bin/
echo "$1 registered in /usr/local/bin"
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x reg
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck reg
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./reg banner
Password:
banner registered in /usr/local/bin
```

## **Задача 6**

Написать программу для проверки наличия комментария в первой строке файлов с расширением c, js и py.

Код `checkcomm`:

```
#!/bin/bash
dir="${1:-.}"

find "$dir" -type f \( -name '*.c' -o -name '*.js' -o -name '*.py' \) -print0 |
while IFS= read -r -d '' file; do
    first=$(head -n 1 "$file")
    case "$file" in
        *.py) pattern='^[[:space:]]*#' ;;
        *)    pattern='^[[:space:]]*(//|/\*)' ;;
    esac

    if [[ $first =~ $pattern ]]; then
        echo "$file: comment found"
    else
        echo "$file: NO comment"
    fi
done
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x checkcomm
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck checkcomm
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./checkcomm
./hello.c: NO comment
```

## **Задача 7**

Написать программу для нахождения файлов-дубликатов (имеющих 1 или более копий содержимого) по заданному пути и подкаталогам.

Код `dups`:

```                         
#!/bin/bash

dir="${1:-.}"

find "$dir" -type f -exec gmd5sum {} + | sort | guniq -w32 --all-repeated=separate
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x dups
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck dups
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % mkdir -p t && echo abc > t/a && echo abc > t/b && echo xyz > t/c && ./dups t
0bee89b07a248e27c83fc3d5951213c1  t/a
0bee89b07a248e27c83fc3d5951213c1  t/b
```

## **Задача 8**

Написать программу, которая находит все файлы в данном каталоге с расширением, указанным в качестве аргумента и архивирует все эти файлы в архив tar.

Код `archext`:

```
#!/bin/bash
if [ $# -lt 1 ]; then
    echo "Usage: $0 extension [dir]" >&2
    exit 1
fi

ext="$1"
dir="${2:-.}"
archive="archive_${ext}.tar"

find "$dir" -type f -name "*.${ext}" -print0 | tar -cvf "$archive" --null -T -
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x archext
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck archext
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./archext c
a ./hello.c
```

## **Задача 9**

Написать программу, которая заменяет в файле последовательности из 4 пробелов на символ табуляции. Входной и выходной файлы задаются аргументами.

Код `sp2tab`:

```
#!/bin/bash
if [ $# -ne 2 ]; then
    echo "Usage: $0 input output" >&2
    exit 1
fi

if [ "$1" = "$2" ]; then
    echo "Error: input and output must differ" >&2
    exit 1
fi

sed 's/    /\t/g' "$1" > "$2"
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x sp2tab 
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck sp2tab
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % ./sp2tab hello.c hello_new.c
```

## **Задача 10**

Написать программу, которая выводит названия всех пустых текстовых файлов в указанной директории. Директория передается в программу параметром.

Код `emptytxt`:

```
#!/bin/bash

if [ $# -ne 1 ] || [ ! -d "$1" ]; then
    echo "Usage: $0 directory" >&2
    exit 1
fi

gfind "$1" -maxdepth 1 -type f -name '*.txt' -empty -printf '%f\n'
```

```
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % chmod +x emptytxt
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % shellcheck emptytxt
mihailborzenkov@MacBook-Air-Mihail-5 practice1 % touch t/e1.txt t/e2.txt; ./emptytxt t
e2.txt
e1.txt
```

## **Выводы**

Работа выполнялась на macOS в командной строке (zsh/bash). Были освоены основные Unix-утилиты: `grep`, `sort`, `cut`, `awk`, `sed`, `tr`, `find`, `tar`, `md5`, `install`. Задачи решались через конвейеры (`|`), где вывод одной утилиты передаётся на вход следующей. Написаны bash-скрипты с проверкой аргументов, выставлением прав доступа (`chmod`, `install -m 755`) и регистрацией команды в `/usr/local/bin`, после чего она доступна из любого каталога. Все скрипты проверены через ShellCheck.

Поскольку в macOS используются **BSD**-версии утилит, а не **GNU** (стандарт для Linux), в нескольких задачах пришлось учитывать различия: у BSD `uniq` и `find` нет флагов `-w`, `--all-repeated`, `-empty`, `-printf`, доступных в GNU. Для решения этих задач были установлены GNU-аналоги через Homebrew (`brew install coreutils`, `brew install findutils`), доступные под именами с префиксом `g` (`gmd5sum`, `guniq`, `gfind`).

По сравнению с Windows (`cmd`) у большинства команд есть аналоги (`dir`/`ls`, `type`/`cat`, `findstr`/`grep`), но набор Unix-утилит на macOS шире и лучше приспособлен для конвейерной работы. В PowerShell конвейеры передают объекты, а не текст, что принципиально отличается от подхода командной строки Unix.
