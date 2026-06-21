--                       ======================================================
--                       ======================================================
--                                   Food Wastage Management System
--                       ======================================================
--                       ======================================================




-- =====================================================
-- set search_path to this schema
-- =====================================================
set search_path to "Food_wastage_mngnt_Sys"



-- =====================================================
-- Create Tables
-- =====================================================

CREATE TABLE providers (
    provider_id INT PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    contact VARCHAR(50)
);


CREATE TABLE receivers (
    receiver_id INT PRIMARY KEY,
    name VARCHAR(255),
    type VARCHAR(100),
    city VARCHAR(100),
    contact VARCHAR(50)
);


CREATE TABLE food_listings (
    food_id INT PRIMARY KEY,
    food_name VARCHAR(255),
    quantity INT,
    expiry_date VARCHAR(50),
    provider_id INT,
    provider_type VARCHAR(100),
    location VARCHAR(100),
    food_type VARCHAR(100),
    meal_type VARCHAR(100),

    CONSTRAINT fk_provider
    FOREIGN KEY (provider_id)
    REFERENCES providers(provider_id)
);

CREATE TABLE claims (
    claim_id INT PRIMARY KEY,
    food_id INT,
    receiver_id INT,
    status VARCHAR(50),
    timestamp VARCHAR(50),

    CONSTRAINT fk_food
    FOREIGN KEY (food_id)
    REFERENCES food_listings(food_id),

    CONSTRAINT fk_receiver
    FOREIGN KEY (receiver_id)
    REFERENCES receivers(receiver_id)
);

-- =====================================================
-- Check if the data is imported or not
-- =====================================================

SELECT COUNT(*) FROM providers;

SELECT COUNT(*) FROM receivers;

SELECT COUNT(*) FROM claims;

SELECT COUNT(*) FROM food_listings;



-- =====================================================
-- Food Providers & Receivers
-- =====================================================


-- === Ques 1: How many food providers and receivers are there in each city? ===--
select
    coalesce(p.city, r.city) as city,
    coalesce(p.total_providers, 0) as total_providers,
    coalesce(r.total_receivers, 0) as total_receivers
from
(
    select
        city,
        count(provider_id) as total_providers
    from providers
    group by city
) p
full outer join
(
    select
        city,
        count(receiver_id) as total_receivers
    from receivers
    group by city
) r
on p.city = r.city
order by city;


-- === Ques 2: Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
select provider_type,
		sum(quantity) as total_food_contributed
	from food_listings
group by provider_type
order by total_food_contributed desc
limit 1


-- === Ques 3: What is the contact information of food providers in a specific city?
-- Replace 'New Jessica' with any city from the dataset.
select provider_id,
		name,
		contact,
		city
	from providers
where city = 'New Jessica'


-- === Ques 4: Which receivers have claimed the most food?
select
    r.receiver_id,
    r.name,
    count(c.claim_id) as total_claims
from claims c
inner join receivers r
on c.receiver_id = r.receiver_id
group by
    r.receiver_id,
    r.name
order by total_claims desc
limit 1;





-- =====================================================
-- Food Listings & Availability
-- =====================================================


-- === Ques 5: What is the total quantity of food available from all providers?
select
	sum(quantity) as total_quantity_of_food
from food_listings


-- === Ques 6: Which city has the highest number of food listings?
select
    location,
    count(food_id) as no_of_food_listings
from food_listings
group by location
order by  no_of_food_listings desc
limit 1;


-- === Ques 7: What are the most commonly available food types?
select
	food_type,
	count(food_id) as total_listings
from food_listings
group by food_type
order by total_listings desc



-- =====================================================
-- Claims & Distribution
-- =====================================================


-- === Ques 8: How many food claims have been made for each food item?
select
	f.food_name as name,
	count(c.food_id) as No_of_claims
from food_listings f
inner join claims c on
f.food_id = c.food_id
group by f.food_name
order by No_of_claims desc;


-- === Ques 9: Which provider has had the highest number of successful food claims?
select
	p.name as name,
	count(c.claim_id) filter (where status = 'Completed') as No_of_successful_claims
from providers p
join food_listings f on
p.provider_id = f.provider_id
join claims c on
f.food_id = c.food_id
group by p.name
order by No_of_successful_claims desc
limit 1


-- === Ques 10: What percentage of food claims are completed vs. pending vs. canceled?
select
	round(
		count(claim_id) filter (where status = 'Completed')::numeric/
		count(claim_id)*100,2) as Completed_percentage,
	round(
		count(claim_id) filter (where status = 'Pending')::numeric/
		count(claim_id)*100,2) as Pending_percentage,
	round(
		count(claim_id) filter (where status = 'Cancelled')::numeric/
		count(claim_id)*100,2) as Cancelled_percentage
from claims
	


-- =====================================================
-- Analysis & Insights
-- =====================================================


-- === Ques 11: What is the average quantity of food claimed per receiver?
select
    r.name,
    round(avg(f.quantity),2) as avg_quantity_of_food_claimed
from receivers r
join claims c on r.receiver_id = c.receiver_id
join food_listings f on f.food_id = c.food_id
group by
    r.receiver_id,
    r.name
order by avg_quantity_of_food_claimed desc


-- === Ques 12: Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?
select
	f.meal_type as Meal_Type,
	count(c.claim_id) as No_of_claims
from food_listings f
inner join claims c on
f.food_id = c.food_id
group by f.meal_type
order by No_of_claims desc
limit 1


-- === Ques 13: What is the total quantity of food donated by each provider?
select
	p.provider_id,
	p.name,
	coalesce(sum(f.quantity),0) as Total_quantity_of_food_donated
from providers p
left join food_listings f on
p.provider_id = f.provider_id
group by p.provider_id, p.name
order by Total_quantity_of_food_donated desc


