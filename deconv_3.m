Y=A(9,:);%A(3,4550:5050);
plot(Y); 
hold on;
Q = movsum(conv(Y, [1 -0.925]),4);
Q=Q;
plot(Q(10:end-5));

