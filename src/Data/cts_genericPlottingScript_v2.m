% Script to plot data from HFSS (in rectangular coordinates)
% - Makes a SEPARATE plot for each csv file provided (rather than
%   superimposing them all on one plot. 

clear all; clc; close all;

%% ======== EDITABLE VARIABLES ======== %%
% You generally should not have to edit any variables outside of this section.

% Folder containing CSV files
folder_path = ""; % Update with the folder path containing CSV files
% Use empty quotes for the folder path if files are in the same directory. 

x_col = 1; % column in data file for the x-axis
y_col = 2; % column in data file for the y-axis

%% ======== PROCESSING ========= %%
% List all CSV files in the folder
csv_files = dir(fullfile(folder_path, "*.csv"));

start_angle = -30;
stop_angle = 29.5; 
step_size = 0.5;
x = start_angle:step_size:stop_angle; 
y = []; 
fop = 1550; 

for k = 1:length(csv_files)
    filename = fullfile(folder_path, csv_files(k).name);
    data = readmatrix(filename);

    
    % Extract the filename without path and extension
    [~, name, ~] = fileparts(filename); % name of file (without .csv)
    index = find(data(:,1) == fop);
    % Extract corresponding y value
    y_value = data(index, y_col);
    if y_value <= 0
        warning("Non-positive y value found in file '%s'. Skipping.", filename);
        continue;
    end
    y(k) = y_value; % Store raw y values for normalization later
end

% Normalize y values with respect to the highest current value
if ~isempty(y)
    max_y = max(y); % Find the highest current value
    normalized_y = y / max_y; % Normalize all y values
    
    % Convert normalized values to dB scale
    y_dB = 10 * log10(normalized_y); 
else
    error("No valid data found for plotting.");
end


% Plotting
figure(1); % Create a new figure for each file
plot(x,y*1e6, 'Linewidth', 3);
hold on;
% Add plot labels
xlabel('Angle');
ylabel('Current (\mu A)');
title("Angular sweep for 1550nm")% Use the filename as the title
xlim ([start_angle stop_angle])

figure(2) 
plot(x,y_dB, 'Linewidth', 3);
hold on;
xlim ([start_angle stop_angle])
% Add plot labels
xlabel('Angle');
ylabel('Normalized Current (dB)');
title("Angular sweep for 1550nm")% Use the filename as the title
% Enable minor ticks for both axes
ax.XAxis.MinorTick = 'on';
ax.YAxis.MinorTick = 'on';

% Specify custom positions for minor ticks
ax.XAxis.MinorTickValues = 0:0.2:10; % Minor ticks every 0.5 units on x-axis
ax.YAxis.MinorTickValues = -1:0.1:1; % Minor ticks every 0.1 units on y-axis
xlim ([start_angle stop_angle])
set(gca, 'FontName', 'Times', 'FontSize', 16, 'LineWidth', 1);
grid on;

fprintf("Plotting %s \n", filename);

fprintf("Done plotting. \n");
fprintf("-------------- \n");
