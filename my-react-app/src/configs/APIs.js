import axios from "axios"

export const BASE_URL= 'http://192.168.1.16:8000/'

export const endpoints ={
 
 
 'register' :'users/',
 'current-user': 'users/current-user/',
 'login' : 'o/token/',

}
export default axios.create({
    baseURL: BASE_URL
});