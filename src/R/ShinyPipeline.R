# loads shiny and reportts it in my python log to confirm shiny step has strated
cat("R shiny pipeline started\n") #cat as no log.log function in python cat prints to stdout which log will pick up
library(shiny)

#load necessery data
#shiny pipelien should always read the latest csv files 
data_dir <- Sys.getenv("SHINY_DATA_DIR")
life_table <- read.csv(file.path(data_dir, "life_table.csv"))


#organiser
#unique() gets all different couuntry codes from data with no duplicates
#all years from data, puts them in order
countries <- unique(life_table$ISO3)
years <- sort(unique(life_table$Year))

#UI
#creates title and sidelayout
#creates drop down menu for countries, with first countr as default
#slider allows user to slect year(s) or period and agerange
#sets bins, with radioButtons giving choice of individual years or custom bins with slider
ui <- fluidPage(
  titlePanel("Population Project V1.0"), # nolint: indentation_linter.
  sidebarLayout(
    sidebarPanel(
      selectInput("country", "Select Country:",
      choices = countries, selected = countries[1]),
      sliderInput("year_range", "select Year Range:",
      min = min(years), max = max(years),
      value = c(min(years), max(years)), step = 1),
      sliderInput("age_range", "select Age Range:",
      min = 0, max = 110,
      value = c(0, 100), step = 1),
      radioButtons("bin_type", "Age Grouping:",
                   choices = c("Individual Years", "Custom Bins"),
                   selected = "Individual Years"),
    
    conditionalPanel(
        condition = "input.bin_type == 'Custom Bins'",
        sliderInput("custom_bins", "Bin Size (years):",
        min = 2, max = 50, value = 5, step = 1)
    )
    ),
    
    mainPanel(
      plotOutput("distPlot")
    )
   )
  )

#the server will create the actual plot
server <- function(input, output, session) {
    #reactive year range for countries
    observe({
        country_data <- life_table[life_table$ISO3 == input$country, ]
        country_years <- sort(unique(country_data$Year))

        updateSliderInput(session, "year_range",
                          min = min(country_years),
                          max = max(country_years),
                          value = c(min(country_years),max(country_years)))
    })

    output$distPlot <- renderPlot({ 
    filtered_data <- life_table[
        life_table$ISO3 == input$country &
        life_table$Year >= input$year_range[1] &
        life_table$Year <= input$year_range[2] &
        life_table$Age >= input$age_range[1] &
        life_table$Age <= input$age_range[2],
    ]
#check if user wants custom bins
if (input$bin_type == "Custom Bins") {
    bin_size <- input$custom_bins
    filtered_data$Age_Binned <- floor(filtered_data$Age / bin_size) * bin_size
    # average lx within each bin and year
    plot_data <- aggregate(lx ~ Age_Binned + Year, data = filtered_data, FUN = mean)
    names(plot_data)[1] <- "Age" #Rename back to age for plotting
}   else{
    #individual years with no bins
    plot_data <- filtered_data[, c("Age","Year", "lx")]
}

# Create the plot------------------------------------------------------------------------------------------------
#color options
colour_choice <- "steelblue"

plot(plot_data$Age, plot_data$lx,
    type = "l", lwd = 2.5, col = colour_choice,
    ylim = c(0,1), #color and line thickness
    bty = "l", #draws LEFT and BOTTOM borders as L shape
    las = 1, #lables axis style 1, y axis numbers horizontal 
    cex.lab = 1.2, #labels 20% bigger 
    cex.main = 1.3, #charcters 30% bigger
    main = paste("Survival Curve (lx) -", input$country),
    xlab = "Age",
    ylab = "lx (Propotion Surviving)")
#multi-year section
if (length(unique(plot_data$Year)) > 1) { #years have to be greater than 1
    years_in_data <- unique(plot_data$Year) #store list of years
    colours <- rainbow(length(years_in_data)) #creates list of colors, make one color for each year
    
    for (i in seq_along(years_in_data)) {
        year_data <- plot_data[plot_data$Year == years_in_data[i], ]#filters to ONE specific years 
        lines(year_data$Age, year_data$lx, col = colours[i], lwd = 2.5) 
    }

    legend("topright", legend = years_in_data, col = colours, lwd = 2.5,
                title = "Year", bty = "n") #creates key, in top right, creates legends, no box surronding
}

    })
}



#sets port number as always 7398 
shinyApp(ui = ui, server = server, options = list(port = 7398))

