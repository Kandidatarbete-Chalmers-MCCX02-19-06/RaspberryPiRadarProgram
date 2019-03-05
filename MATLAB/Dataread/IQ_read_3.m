function [dist,amp_out, phase_out,t,gain, L_start, L_end, L_data, L_seq, Fs] = IQ_read_3(filename)
%IQ_read_3 Is the third iteration of a program to read radar IQ data
%   Reads IQ data from Acconneer radar setup, using the IQ service. The
%   data is first stored in a .csv file using another program, using the
%   format: IQ_format_rect1 The data is then presented in array form for use in
%   signal processing
%
    
    infofilename = strcat('Info_',filename)
    disp('test')

    %delimiter used in document
    delim = ';'
    i_gain = 0;
    j_gain = 1;
        
    i_L_start = 1;
    j_L_start = 1;
        
        
    i_L_end = 2;
    j_L_end = 1;
        
    i_L_data = 3;
    j_L_data = 1;
       
    i_Fs = 4;
    j_Fs = 1;
    
    i_seq = 7;
    j_seq = 1;
    
 
    i_start_of_data = 0;%Seqnr here
    
    t_sim_start = datetime('now');
    
    %Remove parentheses if needed
    try
        dlmread(filename,delim,[i_start_of_data 0 i_start_of_data 0]); %catches if parentheses are present
                                                                                                                                                 
    catch
        disp('removing parentheses')
        fid = fopen(filename,'r+'); %read-and-write permissions
        X = fread(fid);
        X = char(X.');

        % replace parentheses with blank spaces
        Y = strrep(X, '(', ''); 
        Y = strrep(Y, ')', ''); 
        frewind(fid);                       %To overwrite file
        fwrite(fid,Y);
        fclose(fid);
    end
    
    T_parenthesis_removal = datetime('now') - t_sim_start
    
    %Reads 
    gain = dlmread(infofilename,delim,[i_gain j_gain i_gain j_gain]);
    
    L_start = dlmread(infofilename,delim,[i_L_start j_L_start i_L_start j_L_start]);
    L_end = dlmread(infofilename,delim,[i_L_end j_L_end i_L_end j_L_end]);
    L_data = dlmread(infofilename,delim,[i_L_data j_L_data i_L_data j_L_data]);
    Fs  = dlmread(infofilename,delim,[i_Fs j_Fs i_Fs j_Fs]);
    Seq  = dlmread(infofilename,delim,[i_seq j_seq i_seq j_seq]);          %Uncomment for the files where seq exists
    %Seq = Fs*5; %Comment if Seq exists in info file
    
    
    %Time measurement 1
    t_sim_start = datetime('now');
    
    
    %M = csvread(filename,i_start_of_data,0)
    M = dlmread(filename,delim, [0,0,Seq-1,L_data-1]); %Weird data after the last row is added in parentheses removal, not read here
    
    %{
    figure(8)
    plot(M(1,:),'.')
    hold on
    plot(M(2,:),'.')
    plot(M(10,:),'.')
    plot(M(50,:),'.')
    plot(M(600,:),'.')
    hold off
    %}
    
    %Timing of data sorting and reading
    T_data_read_duration = datetime('now') - t_sim_start
    t_sim_start = datetime('now');
    
    amp_out = abs(M);
    phase_out = angle(M);
    
    T_data_sort_duration = datetime('now') - t_sim_start
    
    %Makes 2D grids for 3d display of data
    
    
    
     [L_seq J] = size(amp_out);
    
     distance_vector = linspace(L_start,L_end,L_data);
    
     dist = distance_vector;
    
    t = (0:L_seq-1)/Fs;
    
    [T,D] = meshgrid(t,distance_vector);%2D plane, segment number and distances
    
    for i = 1:L_seq
        A(i,:) = amp_out(i,:);%amp
        P(i,:) = phase_out(i,:);%phase
    end
    A = A';
    P = P';
    
    
    
        
    %L??gg till att breaka o visa felmeddelande ifall null data
    %Fixa fix ifall segement saknas
    
    
    
    
end

