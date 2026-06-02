# Magic Functions Examples

Auto-generated from test_magic_functions.py

## #

| Expression | Result | Description |
|------------|--------|-------------|
| `#()` | `#()` | No argument → None |
| `#(%(json_str))` | `#(%(json_str))` | Valid JSON → parsed object |
| `#(invalid)` | `#(invalid)` | Invalid JSON → None |

## $LEN

| Expression | Result | Description |
|------------|--------|-------------|
| `$LEN(%(name))` | `8` | Length of string |
| `$LEN(%(tags))` | `14` | Length of string with commas |
| `$LEN(%(age))` | `2` | Length of number (as string) |

## $IN

| Expression | Result | Description |
|------------|--------|-------------|
| `$IN(%(status),active,pending)` | `True` | Check if in list |
| `$IN(%(status),inactive,disabled)` | `False` | Not in list |
| `$IN(%(age),25,30,35)` | `True` | Number in list |

## $INI

| Expression | Result | Description |
|------------|--------|-------------|
| `$INI(%(gender),male,female)` | `True` | Case-insensitive match |
| `$INI(%(status),ACTIVE,PENDING)` | `True` | Case-insensitive match |

## $NOW

| Expression | Result | Description |
|------------|--------|-------------|
| `$NOW()` | `2026-04-02 11:47:25` | Current datetime (default format) (e.g., 2026-04-02 11:47:25) |
| `$NOW(%Y-%m-%d)` | `2026-04-02` | Current date only (e.g., 2026-04-02) |

## $DATE

| Expression | Result | Description |
|------------|--------|-------------|
| `$DATE(2024-01-15,%Y-%m-%d)` | `2024-01-15` | Parse date (no reformatting) |
| `$DATE(2024-01-15,%Y-%m-%d,None,None,%d/%m/%Y)` | `15/01/2024` | Parse and reformat |

## $DATE_OFFSET

| Expression | Result | Description |
|------------|--------|-------------|
| `$DATE_OFFSET(2024-01-15,3,months)` | `2024-04-15` | Add 3 months |
| `$DATE_OFFSET(2024-01-15,-1,years)` | `2023-01-15` | Subtract 1 year |
| `$DATE_OFFSET(2024-01-15,1,years,2,months,-5,days)` | `2025-03-10` | Combined offsets |

## $DATE_DIFF

| Expression | Result | Description |
|------------|--------|-------------|
| `$DATE_DIFF(%(survey_date),%(surgery_date),months)` | `5` | Months between dates |
| `$DATE_DIFF(%(survey_date),%(surgery_date),days)` | `152` | Days between dates |
| `$DATE_DIFF(%(survey_date),%(surgery_date),weeks)` | `21` | Weeks between dates |

## $UPPER

| Expression | Result | Description |
|------------|--------|-------------|
| `$UPPER(%(name))` | `JOHN DOE` | Convert to uppercase |

## $LOWER

| Expression | Result | Description |
|------------|--------|-------------|
| `$LOWER(%(name))` | `john doe` | Convert to lowercase |

## $TRIM

| Expression | Result | Description |
|------------|--------|-------------|
| `$TRIM(%(spaced))` | `text` | Trim whitespace |

## $LTRIM

| Expression | Result | Description |
|------------|--------|-------------|
| `$LTRIM(%(spaced))` | `text` | Trim left whitespace |

## $RTRIM

| Expression | Result | Description |
|------------|--------|-------------|
| `$RTRIM(%(spaced))` | `text` | Trim right whitespace |

## $SUBSTR

| Expression | Result | Description |
|------------|--------|-------------|
| `$SUBSTR(%(patient_id),0,5)` | `P1234` | Extract first 5 chars |
| `$SUBSTR(%(patient_id),1)` | `12345` | Extract from position 1 |

## $CONCAT

| Expression | Result | Description |
|------------|--------|-------------|
| `$CONCAT(%(first_name), ,%(last_name))` | `JohnDoe` | Concatenate with space |

## $STARTSWITH

| Expression | Result | Description |
|------------|--------|-------------|
| `$STARTSWITH(%(patient_id),P)` | `True` | Check if starts with |

## $ENDSWITH

| Expression | Result | Description |
|------------|--------|-------------|
| `$ENDSWITH(%(patient_id),5)` | `True` | Check if ends with |

## $CONTAINS

| Expression | Result | Description |
|------------|--------|-------------|
| `$CONTAINS(%(name),Doe)` | `True` | Check if contains |

## $MATCH

| Expression | Result | Description |
|------------|--------|-------------|
| `$MATCH(%(period),Pre-?Op)` | `True` | Regex match |

## $SPLIT

| Expression | Result | Description |
|------------|--------|-------------|
| `$SPLIT(%(name),$CHR(32))` | `['John', 'Doe']` | Split by space using CHR(32) |
| `$SPLIT(%(name),$CHR(32),0)` | `John` | Split by space, get element 0 |
| `$SPLIT(%(tags),$CHR(44))` | `['tag1', 'tag2', 'tag3']` | Split by comma using CHR(44) |
| `$SPLIT(%(tags),$CHR(44),0)` | `tag1` | Split by comma, get element 0 |

## $JOIN

| Expression | Result | Description |
|------------|--------|-------------|
| `$JOIN($SPLIT(%(name),$CHR(32)),;)` | `John;Doe` | Split by space, join with semicolon |

## $CHR

| Expression | Result | Description |
|------------|--------|-------------|
| `$CHR(44)` | `,` | Comma character |
| `$CHR(65)` | `A` | Uppercase A |
| `$CHR(32)` | ` ` | Space character |

## $EQ

| Expression | Result | Description |
|------------|--------|-------------|
| `$EQ(%(age),25)` | `True` | Equal |

## $NE

| Expression | Result | Description |
|------------|--------|-------------|
| `$NE(%(age),30)` | `True` | Not equal |

## $LT

| Expression | Result | Description |
|------------|--------|-------------|
| `$LT(%(age),30)` | `True` | Less than |

## $LE

| Expression | Result | Description |
|------------|--------|-------------|
| `$LE(%(age),25)` | `True` | Less than or equal |

## $GT

| Expression | Result | Description |
|------------|--------|-------------|
| `$GT(%(age),20)` | `True` | Greater than |

## $GE

| Expression | Result | Description |
|------------|--------|-------------|
| `$GE(%(age),25)` | `True` | Greater than or equal |

## $EQI

| Expression | Result | Description |
|------------|--------|-------------|
| `$EQI(%(gender),male)` | `True` | Equal (case-insensitive) |

## $NEI

| Expression | Result | Description |
|------------|--------|-------------|
| `$NEI(%(status),INACTIVE)` | `True` | Not equal (case-insensitive) |

## $IF

| Expression | Result | Description |
|------------|--------|-------------|
| `$IF($GT(%(age),18),adult,minor)` | `adult` | Conditional: adult |
| `$IF($LT(%(age),18),adult,minor)` | `minor` | Conditional: minor |

## $AND

| Expression | Result | Description |
|------------|--------|-------------|
| `$AND($GT(%(age),18),$EQ(%(status),active))` | `True` | AND: both true |

## $OR

| Expression | Result | Description |
|------------|--------|-------------|
| `$OR($LT(%(age),18),$EQ(%(status),active))` | `True` | OR: one true |

## $NOT

| Expression | Result | Description |
|------------|--------|-------------|
| `$NOT($EQ(%(status),inactive))` | `True` | NOT: invert |

## $Z

| Expression | Result | Description |
|------------|--------|-------------|
| `$Z()` | `True` | Check empty (no arg) returns True |

## $N

| Expression | Result | Description |
|------------|--------|-------------|
| `$N(%(name))` | `True` | Check non-empty |

## $FIRST_N

| Expression | Result | Description |
|------------|--------|-------------|
| `$FIRST_N(,%(name),default)` | `John Doe` | First non-empty (skip empty) |

## $FIRST_Z

| Expression | Result | Description |
|------------|--------|-------------|
| `$FIRST_Z(%(name),,other)` | `` | First empty (skip non-empty) |

## $PLUS

| Expression | Result | Description |
|------------|--------|-------------|
| `$PLUS(%(score1),%(score2))` | `30` | Add two numbers |
| `$PLUS(1,2,3,4)` | `10` | Add multiple numbers |

## $MINUS

| Expression | Result | Description |
|------------|--------|-------------|
| `$MINUS(100,10,5)` | `85` | Subtract multiple |

## $MULTIPLY

| Expression | Result | Description |
|------------|--------|-------------|
| `$MULTIPLY(2,3,4)` | `24` | Multiply multiple |

## $DIVIDE

| Expression | Result | Description |
|------------|--------|-------------|
| `$DIVIDE(100,2,5)` | `10.0` | Divide multiple |

## $MODULO

| Expression | Result | Description |
|------------|--------|-------------|
| `$MODULO(%(age),10)` | `5` | Modulo |

## $ABS

| Expression | Result | Description |
|------------|--------|-------------|
| `$ABS(-42)` | `42` | Absolute value |

## $MIN

| Expression | Result | Description |
|------------|--------|-------------|
| `$MIN(%(score1),%(score2),5)` | `5` | Minimum value |

## $MAX

| Expression | Result | Description |
|------------|--------|-------------|
| `$MAX(%(score1),%(score2),5)` | `20` | Maximum value |

## $ROUND

| Expression | Result | Description |
|------------|--------|-------------|
| `$ROUND(3.14159,2)` | `3.14` | Round to 2 decimals |

## $EVEN

| Expression | Result | Description |
|------------|--------|-------------|
| `$EVEN(%(age))` | `False` | Check if even |

## $ODD

| Expression | Result | Description |
|------------|--------|-------------|
| `$ODD(%(age))` | `True` | Check if odd |

## $POWER

| Expression | Result | Description |
|------------|--------|-------------|
| `$POWER(2,3)` | `8` | 2 to the power of 3 |
| `$POWER(10,2)` | `100` | 10 squared |
| `$POWER(2,2,2)` | `16` | 2^2^2 (variadic) |

## $MD5

| Expression | Result | Description |
|------------|--------|-------------|
| `$MD5(%(patient_id))` | `$MD5(%(patient_id))` | MD5 hash of single value (32 chars) |
| `$MD5(%(patient_id),%(date))` | `$MD5(%(patient_id),%(date))` | MD5 of concatenated values (32 chars) |

## $UUID

| Expression | Result | Description |
|------------|--------|-------------|
| `$UUID()` | `ab4cd552-fbd3-49d9-b9c7-316d9e508dd9` | Generate UUID (36 chars) |


