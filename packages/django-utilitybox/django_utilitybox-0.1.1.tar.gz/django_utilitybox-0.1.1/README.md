# Django Utilitybox
![Logo](https://i.imgur.com/KXosc2D.png)


Managment software by 'On road Rescues': Stable Version.

## Installation

```bash
  pip install django-utilitybox
```

## Usage

### Raise Exception

```python
  from django_utilitybox.response import raise_response as rres
```

This utility makes it easier to return errors in DRF.
Giving a default message and a status.
The options are as follows.


| Class | Status | Message | Use cases |
| :-------- | :------- | :------- |  :------- |
| `QueryParamNotFound` | 400 | `Queryparam '{field}' is required` | Used when a query param is not found in the url |
| `KwargNotFound ` | 400 | `Kwarg '{field}' is required` | Used when a kwarg is not found |
| `ModelNotFound` | 400 | `{field} don't exist` | Used when a model is not found |
| `CustomRaise` | 400 | `   ` | Se usa cuando se quiere mandar un mensaje personalizado |
####  Use cases

```python
	 class  ResponseTest(APIView):
		def  get(self, *args, **kwargs):
		data:dict  =  self.request.GET
		param  =  data.get('case')
		match  param:
			case  '1': rres.QueryParamNotFound('id')
			case  '2': rres.KwargNotFound ('data')
			case  '3': rres.ModelNotFound('Rescue')
			case  '4': rres.CustomRaise('Custom message')
		return  Response({'message': 'Successful.'}, status=st.HTTP_200_OK)
```
### Returns
| Class | Status | Message |
| :-------- | :------- | :------- | 
| `QueryParamNotFound` | 400 | `Queryparam 'id' is required` |
| `KwargNotFound ` | 400 | `Kwarg 'data' is required` |
| `ModelNotFound` | 400 | `Rescue don't exist` |
| `CustomRaise` | 400 | `Custom message` |

### Json returned
```json
HTTP 400 Bad Request
{
	"status":  "{message}"
}
```
### Modifiable parameters

WIP

***
## Used By

This project is used by the following companies:

- AETO Software