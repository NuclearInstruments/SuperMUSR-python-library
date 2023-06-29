plot(A2(2,1910:2100)); 
hold on;
Q = movsum(conv(A2(2,1900:2100), [1 -0.928]),5);
plot(Q(10:end-5));

plot(A4(2,1910:2100)); 
hold on;
Q = movsum(conv(A4(2,1900:2100), [1 -0.928]),5);
plot(Q(10:end-5));

