var tpl_createDetailTable = "<table id=<%= ids %> class=<%= classes %> style=<%= styles %>>
                                <thead>
                                    <tr>
                                        <% _.each(ths, function(widths, titles){%>  
                                                        <th align=\"left\" width=<%= widths %>><%= titles %></th>
                                                 <%}); %>
                                    </tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>";