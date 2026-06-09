-- Q1: All successful bookings
SELECT * FROM bookings WHERE Booking_Status = 'Success';

-- Q2: Average ride distance per vehicle type
SELECT Vehicle_Type, AVG(Ride_Distance) AS avg_distance
FROM bookings GROUP BY Vehicle_Type;

-- Q3: Total cancelled rides by customers
SELECT COUNT(*) AS customer_cancellations
FROM bookings WHERE Booking_Status = 'Canceled by Customer';

-- Q4: Top 5 customers by number of rides
SELECT Customer_ID, COUNT(*) AS total_rides
FROM bookings GROUP BY Customer_ID
ORDER BY total_rides DESC LIMIT 5;

-- Q5: Driver cancellations due to personal/car issues
SELECT COUNT(*) AS count FROM bookings
WHERE Booking_Status = 'Canceled by Driver'
AND Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- Q6: Max and min driver ratings for Prime Sedan
SELECT MAX(Driver_Ratings) AS max_rating, MIN(Driver_Ratings) AS min_rating
FROM bookings WHERE Vehicle_Type = 'Prime Sedan';

-- Q7: All rides paid by UPI
SELECT * FROM bookings WHERE Payment_Method = 'UPI';

-- Q8: Average customer rating per vehicle type
SELECT Vehicle_Type, AVG(Customer_Rating) AS avg_customer_rating
FROM bookings GROUP BY Vehicle_Type;

-- Q9: Total booking value for successful rides
SELECT SUM(Booking_Value) AS total_revenue
FROM bookings WHERE Booking_Status = 'Success';

-- Q10: All incomplete rides with reasons
SELECT Booking_ID, Vehicle_Type, Pickup_Location,
       Drop_Location, Incomplete_Rides_Reason
FROM bookings WHERE Incomplete_Rides = 'Yes';