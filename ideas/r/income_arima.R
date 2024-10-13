in_ln <- log(lulu[["net_income"]])
in_diff <- c(diff(in_ln))

denorm <- function(s) {
  exp(c(diffinv(s, differences=1, xi=in_ln[1])))
}

ggtsdisplay(in_diff, main="")
(fit <- Arima(in_diff, order=c(0,1,4), seasonal=c(0,1,1)))
checkresiduals(fit)
autoplot(forecast(fit))
forecast(fit, h=16)
denorm(c(in_diff, forecast(fit, h=16)$mean))
lulu[["net_income"]]
