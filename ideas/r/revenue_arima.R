rev_ln <- log(lulu[["revenue"]])
rev_diff <- c(diff(rev_ln, differences=2))

denorm <- function(s) {
  exp(c(diffinv(s, differences=2, xi=rev_ln[1:2])))
}

ggtsdisplay(rev_diff, main="")
(fit <- arima(rev_diff, order=c(0,2,4), seasonal=c(0,2,1)))
checkresiduals(fit)
autoplot(forecast(fit))
denorm(c(rev_diff, forecast(fit)$mean))
lulu[["revenue"]]
