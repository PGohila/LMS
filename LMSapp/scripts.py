
def success_response(message): # return success_message
    try:
        response = {'status_code':0,'data':message}
        return response
    except Exception as error:
        print(f"{str(error)}")

def fail_response(message): #  return fail_message
    try:
        response = {'status_code':1,'data':message}
        return response
    except Exception as error:
        print(f"{str(error)}")