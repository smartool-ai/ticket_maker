import React, { useState } from 'react';
import { CardElement, PaymentElement, useStripe, useElements } from '@stripe/react-stripe-js';

const Payment = () => {
    const stripe = useStripe();
    const elements = useElements();
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(false);
    const [paymentInfo, setPaymentInfo] = useState({
        name: '',
        email: '',
        address: '',
    });


    const handleSubmit = async (event) => {
        event.preventDefault();

        setLoading(true);

        const { error, paymentMethod } = await stripe.createPaymentMethod({
            type: 'card',
            card: elements.getElement(CardElement),
            billing_details: {
                name: paymentInfo.name,
                email: paymentInfo.email,
                address: {
                    line1: paymentInfo.address,
                },
            },
        });

        setLoading(false);

        if (error) {
            setError(error.message);
        } else {
            // Handle successful payment
            console.log(paymentMethod);
        }
    };

    const handleChange = (event) => {
        setPaymentInfo({
            ...paymentInfo,
            [event.target.name]: event.target.value,
        });
    };

    const submitButton = () => {
        return (
        <div>
            <button
            id="submitButton"
            type="button"
            onClick={() => handleSubmit()}
            className="rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-[#4654A3] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-600"
            >
            Submit
            </button>
        </div>
        )
    };

    return (
        <form onSubmit={handleSubmit}>
            <div>
                <label>
                    Name
                    <input type="text" name="name" value={paymentInfo.name} onChange={handleChange} />
                </label>
            </div>
            <div>
                <label>
                    Email
                    <input type="email" name="email" value={paymentInfo.email} onChange={handleChange} />
                </label>
            </div>
            <div>
                <label>
                    Address
                    <input type="text" name="address" value={paymentInfo.address} onChange={handleChange} />
                </label>
            </div>
            <div>
                <label>
                    Card details
                    <CardElement />
                </label>
            </div>
            {error && <div>{error}</div>}
            <button type="submit" disabled={!stripe || loading}>
                Pay
            </button>
        </form>
    );
};

export default Payment;