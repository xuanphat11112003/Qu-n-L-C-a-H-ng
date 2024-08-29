const MyUserReducer = (currentState, action) => {
    switch (action.type) {
        case "login":
            return {
                ...currentState,
                ...action.payload
            };
        case "logout":
            localStorage.removeItem('access_token');
            localStorage.removeItem('username');
            localStorage.removeItem('avatar');
            localStorage.removeItem('fisrtname');
            sessionStorage.removeItem('access_token');
            return null;
        default:
            return currentState; 
    }
}

export default MyUserReducer;
