import React, { useState } from 'react';
import Payment from "../components/Payment";
import { Elements } from '@stripe/react-stripe-js';
import {loadStripe} from '@stripe/stripe-js';

// console.log('REACT_APP_STRIPE_PUBLIC_KEY:', __REACT_APP_STRIPE_PUBLIC_KEY__);
// const stripePromise = loadStripe(__REACT_APP_STRIPE_PUBLIC_KEY__);

export default function UserSettings() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    // const stripeOptions = {
    //     clientSecret: __REACT_APP_STRIPE_CLIENT_SECRET__,
    // }

    const handleNameChange = (e) => {
        setName(e.target.value);
    };

    const handleEmailChange = (e) => {
        setEmail(e.target.value);
    };

    const handlePasswordChange = (e) => {
        setPassword(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        // Add your logic here to update user settings
    };

    return (

        // <Elements stripe={stripePromise} options={stripeOptions}>
        <div>
            <h1>User Settings</h1>
            <form onSubmit={handleSubmit}>
                <label>
                    Name:
                    <input type="text" value={name} onChange={handleNameChange} />
                </label>
                <br />
                <label>
                    Email:
                    <input type="email" value={email} onChange={handleEmailChange} />
                </label>
                <br />
                <label>
                    Password:
                    <input type="password" value={password} onChange={handlePasswordChange} />
                </label>
                <br />
                <button type="submit">Save</button>
            </form>
            {/* <Payment /> */}
        </div>
        // </Elements>
    );
};
